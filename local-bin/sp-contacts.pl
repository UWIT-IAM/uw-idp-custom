#!/usr/local/bin/perl

# scan rp filter files for entity ids we deal with
# scan metadata files for related admins
# accumulate email list
# update appropriate group
# update web page

use File::Copy;
use XML::DOM;
use Crypt::SSLeay;
use LWP::UserAgent;
use LWP::Simple;

# ------------------- parameters ------------

# filter and metadata files
my $rp_filter_file = "/data/local/idp/conf/rp-filter.xml";
my $uw_metadata_file = "/data/local/idp/tmp/uwmd.xml";
my $ic_metadata_file = "/data/local/idp/tmp/icmd.xml";

## see end of file
# mebers of this group are contacts
my $group_name = "";
my $gws_group_url = "";

# webpage
my $webpage_file = "";
my $webpage_file_tmp = ".tmp";

# authentication
# $ENV{HTTPS_CA_FILE} = "/data/local/idp/credentials/uwca.crt";
$ENV{HTTPS_CA_FILE} = "/usr/local/ssl/certs/cacerts.cert";
$ENV{HTTPS_CERT_FILE} = "/data/local/idp/credentials/idp-uw.crt";
$ENV{HTTPS_KEY_FILE}  = "/data/local/idp/credentials/idp-uw.key";


# -------------------------------------------

my $parser = XML::DOM::Parser->new();

# splist is list of all sps we are interested in
# hash ( 'entityid' -> 1 )
my %splist;
my $nsp = 0;

# contacts is list of the contact people from the splist sps
# hash ( 'email' -> (name, entityid, mdsrc) )
my %contacts;
my $ncontacts = 0;

# members is membership of the gws group
# hash ( 'email' -> 'old|ok' )
my %members;
my $nmembers = 0;

# --------------------------------------------
sub trim($) {
   my $string = shift;
   $string =~ s/^\s+//;
   $string =~ s/\s+$//;
   return $string;
}

# convert obvious uw emails to uwnetids
sub clean_email {
   my $em = trim($_[0]);
   $em =~ s/\@u\.washington\.edu$//;
   $em =~ s/\@cac\.washington\.edu$//;
   $em =~ s/\@washington\.edu$//;
   $em =~ s/\@uw\.edu$//;
   if ($em =~ m/\@/ ) {
      return $em;
   }
   # lowercase idiot cap netids
   return lc $em;
}


#----------------------------------------------

# gather sp entities from filter files
# ignore uw sites here

sub parseFilter {
  my $ffile = $_[0];
  my $doc = $parser->parsefile($ffile);
  
  foreach my $afp ($doc->getElementsByTagName('AttributeFilterPolicy')){
   
     # get the rp entity id
     my $prr = $afp->getElementsByTagName('PolicyRequirementRule')->item(0);
     my $rp = $prr->getAttribute('value');

     if ($rp eq '') {
       # print "don't handle multiple rps\n";
       next;
     }
     if ($rp =~ m/\.washington\.edu\//) {
        # print "skip $rp\n";
        next;
     }
     if ($rp =~ m/\.uw\.edu\//) {
        # print "skip $rp\n";
        next;
     }
     
     $splist{$rp} = 1;
     $nsp++;
  }
}


# ---------------------------------------------

# scan metadata for flagged sps

my %spents;

sub parseMetadata {
  my $ffile = $_[0];
  my $src = $_[1];
  my $doc = $parser->parsefile($ffile);
  
  my $seq = 0;
  foreach my $ed ($doc->getElementsByTagName('EntityDescriptor')){
   
     # get the rp entity id
     my $rp = $ed->getAttribute('entityID');
     my $spl = $ed->getElementsByTagName('SPSSODescriptor');
     if ( defined $spl) {
        # one of ours?
        if ( $rp=~m/\.washington\.edu\// || $rp=~m/\.uw\.edu\// || exists $splist{$rp} ) {
           # get the contacts
           foreach my $ct ( $ed->getElementsByTagName('ContactPerson')) {
              if ( ! defined $ct ) {
                 # print "no contacts\n";
                 next;
              }
              # see if there's a name ( GivenName )
              my $nm = '';
              my $nme = $ct->getElementsByTagName('GivenName')->item(0);
              if ( defined $nme ) {
                 $nm = $nme->getFirstChild()->getNodeValue();
                 # print "name is: $nm,  ";
              }
              my $eme = $ct->getElementsByTagName('EmailAddress')->item(0);
              if ( defined $eme ) {
                 my $em = clean_email($eme->getFirstChild()->getNodeValue());
                 # check valid 
                 my $xx = $em;
                 $xx =~ s/^.*\@//;
                 if ( $xx =~ m/[^a-z0-9\.-]/ )  {
                    print "bogus email: $em\n";
                    next;
                 }
                 my @contact = ($nm, $rp, $src);
                 @{$contacts{$em}} = @contact;
                 # print "ct is: $contact[0] = $contact[1]\n";
                 my $k = $em . $seq;
                 @{$spents{$k}} = ($nm, $rp, $src, $em);
                 $seq += 1;
              }
           }
        }
     }
  }
}
     
# --------------------------------------------

# update web page

sub updateWebpage {
  open (HTML, ">" . $webpage_file_tmp);

  my $nt = scalar localtime();
  print HTML "Generated from metadata on $nt<ul class=\"sptable\">\n";

  my $lem = '';
  my $lnm = '';
  my %sps = ();
  foreach $k (sort {"\L$a" cmp "\L$b"} (keys %spents)) {
     my @d = @{$spents{$k}};
     my $em = $d[3];
     if ($em eq $lem) {
        if ($d[0] ne '') {
           $lnm = $d[0];
        }
        $sps{$d[1]} = $d[2];
     } else {
        if ($lem ne '') {
            print HTML "<li><span class=\"netid\">$lem</span><span class=\"name\">($lnm)</span><ul>";
            foreach $k (sort(keys %sps)) {
              print HTML " <li>$k</li>\n";
            }
            print HTML "</ul></li>\n";
        }
        $lem = $em;
        $lnm = $d[0];
        %sps = ();
        $sps{$d[1]} = $d[2];
     }
  }
  # print last row
  print HTML "<li><span class=\"netid\">$lem</span><span class=\"name\">($lnm)</span></li>";
  foreach $k (sort(keys %sps)) {
        print HTML " <li>$k</li>\n";
  }
  print HTML "</ul></li></ul>\n";

  close(HTML);
  move ($webpage_file_tmp, $webpage_file);

}



# -----------------------------------------

# tools to work with GWS

# $ENV{HTTPS_DEBUG} = 1;

my $agent = LWP::UserAgent->new(ssl_opts => { 
                    SSL_ca_file         => '/data/local/idp/credentials/uwca.crt',
                    SSL_cert_file       => '/data/local/idp/credentials/idp-uw.crt',
                    SSL_key_file        => '/data/local/idp/credentials/idp-uw.key'
                   }
                ); 
# ssl_opts => { verify_hostname => 0 }


# get current group membership ( we collect only eppn (email))

sub getMembers {
   my @hdrs = ('Accept' => 'text/xml');
   my $response = $agent->get( $gws_group_url, @hdrs );

   if ( $response->is_success ) {
   
     print "get members status: $response->code\n";

     $xml = trim($response->decoded_content());
     my $doc = $parser->parse($xml);

     my $grp = $doc->getElementsByTagName('group')->item(0);
     my $mbrse = $grp->getElementsByTagName('members')->item(0);
     foreach my $mbre ($mbrse->getElementsByTagName('member')){
        my $type = $mbre->getAttribute('type');
        my $mbr = $mbre->getFirstChild()->getNodeValue();
        # print "type=$type, mbr=$mbr\n";
        if ($type eq 'eppn' || $type eq 'uwnetid') {
           $members{$mbr} = "old";
           $nmembers++;
        }
      }
   } else {
     print "Membership fetch failed!\n";
   }
   print "found $nmembers eppn members\n";
   
}

# compare the new vs old memberships

# comma separated lists for PUT to GWS
my $newmembers = "";
my $oldmembers = "";
my $nnew = 0;
my $nold = 0;
my $nkeep = 0;

sub compareMembers() {

  foreach $k (keys %contacts) {
   if (exists $members{$k}) {
      # print "$k already there\n";
      $members{$k} = "ok";
   } else {
      print "adding $k\n";
      if ($nnew==0) {
         $newmembers = $k;
      } else {
         $newmembers = $newmembers . ',' . $k;
      }
      $nnew++;
   }
  }

  foreach $k (keys %members) {
     if ($members{$k} eq 'old') {
      print "dropping $k\n";
      if ($nold==0) {
         $oldmembers = $k;
      } else {
         $oldmembers = $oldmembers . ',' . $k;
      }
      $nold++;
     } else {
        $nkeep++;
     }
  }
 
  print "adding $nnew\n";
  print "dropping $nold\n";
  print "keeping $nkeep\n";
}

# update group memberships

sub updateMembers {
   # put new
  if ($nnew>0) {
   my $put = HTTP::Request->new(PUT => $gws_group_url . $newmembers);
   my $response = $agent->request( $put );
   my $rsp = $response->code;
   if ( $response->is_success ) {
      print "put resp: $rsp\n";
      $xml = trim($response->decoded_content());
      # print "\[ $xml \]\n";
   } else {
      print "put failed: $rsp\n";
   }
  }

   # delete old
  if ($nold>0) {
   my $del = HTTP::Request->new(DELETE => $gws_group_url . $oldmembers);
   my $response = $agent->request( $del );
   my $rsp = $response->code;
   if ( $response->is_success ) {
      print "del resp: $rsp\n";
      $xml = trim($response->decoded_content());
      print "\[ $xml \]\n";
   } else {
      # print "del failed: $rsp\n";
   }
  }
}


#
# -----------------------------------------------------
#
# Main
#


# make the group and list for uw only

parseFilter($rp_filter_file);
parseMetadata ($uw_metadata_file, 'uw');

$group_name = "u_weblogin_sp-contacts-uw";
$gws_group_url = "https://iam-ws.u.washington.edu/group_sws/v2/group/u_weblogin_sp-contacts-uw/member/";
$webpage_file = "/www/sp-contacts/sp-contacts-uw.html";
$webpage_file_tmp = $webpage_file . ".tmp";


# get existing membership
getMembers();

# compare and update
compareMembers();
updateMembers();
updateWebpage();

# add the incommon folk
%members = {};
$nmembers = 0;
$newmembers = "";
$oldmembers = "";
$nnew = 0;
$nold = 0;
$nkeep = 0;

parseMetadata ($ic_metadata_file, 'ic');
$group_name = "u_weblogin_sp-contacts";
$gws_group_url = "https://iam-ws.u.washington.edu/group_sws/v2/group/u_weblogin_sp-contacts/member/";
$webpage_file = "/www/idp-dev.u.washington.edu/sp-contacts/sp-contacts.html";
$webpage_file_tmp = $webpage_file . ".tmp";

# get existing membership
getMembers();

# compare and update
compareMembers();
print "$newmembers\n";
print "$oldmembers\n";
updateMembers();
updateWebpage();


