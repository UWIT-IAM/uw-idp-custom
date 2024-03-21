<flow xmlns="http://www.springframework.org/schema/webflow" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.springframework.org/schema/webflow http://www.springframework.org/schema/webflow/spring-webflow.xsd"
    parent="authn.abstract">
    
    <!-- This is a simple login flow for Duo Bypass. -->

    <view-state id="DuoBypassView" view="duo-bypass">
        <on-render>
            <evaluate expression="environment" result="viewScope.environment" />
            <evaluate expression="flowRequestContext.getExternalContext().getNativeRequest()" result="viewScope.request" />
            <evaluate expression="flowRequestContext.getExternalContext().getNativeResponse()" result="viewScope.response" />
            <evaluate expression="flowRequestContext.getActiveFlow().getApplicationContext().containsBean('shibboleth.CustomViewContext') ? flowRequestContext.getActiveFlow().getApplicationContext().getBean('shibboleth.CustomViewContext') : null" result="viewScope.custom" />
        </on-render>

        <transition on="proceed" to="PreValidateDuoBypass" />
        <transition on="cancel" to="ReselectFlow" />
        <!-- <transition on-exception="edu.washington.shibboleth.authn.entrust.AuthnException" to="AuthenticationException" /> -->
    </view-state>


    <action-state id="PreValidateDuoBypass">
        <evaluate expression="flowRequestContext.getExternalContext().getNativeRequest()" result="flowScope.request" />
        <evaluate expression="flowScope.request.getParameter('fp_value')" result="conversationScope.fingerprint" />
        <evaluate expression="flowScope.request.getParameter('fpt_value')" result="conversationScope.fptime" />
        <evaluate expression="'proceed'" />
        <transition on="proceed" to="ValidateDuoBypass" />
    </action-state>

    <action-state id="ValidateDuoBypass">
        <evaluate expression="ValidateDuoBypass" />
        <evaluate expression="'proceed'" />
        
        <transition on="proceed" to="proceed" />
    </action-state>

    <action-state id="LogDuoException">
        <on-entry>
            <evaluate expression="T(org.slf4j.LoggerFactory).getLogger('net.shibboleth.idp.authn.duo').error('DuoWebException', flowExecutionException.getCause())" />
        </on-entry>
        <evaluate expression="'AuthenticationException'" />
    </action-state>

    <bean-import resource="duo-bypass-beans.xml" />

</flow>
