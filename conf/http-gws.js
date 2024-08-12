/* HTTP dataconnector json response interpreter */

  // debugging tools
  // var Excp = Java.type("java.lang.Exception");
  logger = Java.type("org.slf4j.LoggerFactory").getLogger("net.shibboleth.idp.attribute");
  // logger.info("=== gws in");
  //  new Excp().printStackTrace();

  var ArrayList = Java.type("java.util.ArrayList");
  var HttpClientSupport = Java.type("net.shibboleth.shared.httpclient.HttpClientSupport");
  var IdPAttribute = Java.type("net.shibboleth.idp.attribute.IdPAttribute");
  var StringAttributeValue = Java.type("net.shibboleth.idp.attribute.StringAttributeValue");
   
  var body = HttpClientSupport.toString(response.getEntity(), "UTF-8", 1000000);
  var result = JSON.parse(body);

  var attr = new IdPAttribute("memberOf");
  var values = new ArrayList();
  if (result.data != null) {
      logger.info("GWS: " + result.data.length + " groups");
      for (var i=0; i<result.data.length; i++) {
        // logger.info(new StringAttributeValue(result.data[i].id));
        values.add(new StringAttributeValue(result.data[i].id));
      }
  }
  attr.setValues(values);
  connectorResults.add(attr);
  // logger.info("in http-gws.js; connectorResults: " + connectorResults);
  // logger.info("=== gws out");
