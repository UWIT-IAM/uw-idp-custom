/* HTTP dataconnector json response interpreter for PWS */

  // debugging tools
  // var Excp = Java.type("java.lang.Exception");
  logger = Java.type("org.slf4j.LoggerFactory").getLogger("net.shibboleth.idp.attribute");
  logger.info("=== pws in");
  // new Excp().printStackTrace();

  var HashSet = Java.type("java.util.HashSet");
  var HttpClientSupport = Java.type("net.shibboleth.shared.httpclient.HttpClientSupport");
  var IdPAttribute = Java.type("net.shibboleth.idp.attribute.IdPAttribute");
  var StringAttributeValue = Java.type("net.shibboleth.idp.attribute.StringAttributeValue");
   
  var body = HttpClientSupport.toString(response.getEntity(), "UTF-8", 1000000);
  var pws = JSON.parse(body);

  // function to add item to results
  var addItem = function(src, name) {
     if (src==null) return;
     logger.info(". attr " + name);
     var values = new HashSet(); 
     var attr = new IdPAttribute(name);
     values.add(new StringAttributeValue(src));
     attr.setValues(values);
     connectorResults.add(attr);
  }
  // function to add item to results
  var addItems = function(src, name) {
     if (src==null) return;
     logger.info(". attr " + name);
     var values = new HashSet(); 
     var attr = new IdPAttribute(name);
     for (x in src) {
        logger.info(".. adding " + src[x]);
        values.add(new StringAttributeValue(src[x]));
     }
     attr.setValues(values);
     connectorResults.add(attr);
  }

  // basic attrs
  
  addItem(pws.UWNetID, "uwNetID");
  addItem(pws.UWRegID, "uwRegID");

  addItem(pws.DisplayName, "DisplayName");
  addItem(pws.RegisteredName, "RegisteredName");
  addItem(pws.RegisteredSurname, "RegisteredSurname");
  addItem(pws.RegisteredFirstMiddleName, "RegisteredFirstMiddleName");
  addItem(pws.PreferredSurname, "PreferredSurname");
  addItem(pws.PreferredFirstName, "PreferredFirstName");
  addItem(pws.PreferredMiddleName, "PreferredMiddleName");

  addItems(pws.EduPersonAffiliations, "EduPersonAffiliations");

  // person attrs

  if (pws.PersonAffiliations != null) {
     // employee
     var epa = pws.PersonAffiliations.EmployeePersonAffiliation;
     if (epa != null) {
        addItem(epa.HomeDepartment, "HomeDepartment");
        addItem(epa.MailStop, "MailStop");
        addItem(epa.EmployeeID, "EmployeeID");
        var ewp = epa.EmployeeWhitePages;
        if (ewp != null) {
           if (ewp.Phones != null) addItem(ewp.Phones[0], "EPWPhone1");
           if (ewp.EmailAddresses != null) addItem(ewp.EmailAddresses[0], "EPWEmail1");
           if (ewp.Positions != null) {
              logger.info(".. positions");
              for (x in ewp.Positions) {
                if (ewp.Positions[x].Primary != null && ewp.Positions[x].Primary) {
                   addItem(ewp.Positions[x].EWPTitle, "EWPTitle1");
                }
              }
           }
           
        }
     }
     // student
     var spa = pws.PersonAffiliations.StudentPersonAffiliation;
     if (spa != null) {
        addItem(spa.StudentNumber, "StudentNumber");
        addItem(spa.StudentSystemKey, "StudentSystemKey");
        var swp = spa.StudentWhitePages;
        if (swp != null) {
           addItem(swp.Phone, "SWPPhone");
           addItem(swp.Email, "SWPEmail");
           if (swp.Positions != null) {
              logger.info(".. positions");
              for (x in ewp.Positions) {
                if (ewp.Positions[x].Primary != null && ewp.Positions[x].Primary) {
                   addItem(ewp.Positions[x].EWPTitle, "EWPTitle1");
                }
              }
           }
           
        }
     }

  }
  logger.info("=== pws out");
