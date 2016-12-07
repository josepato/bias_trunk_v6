
/**
 * FactWSFrontCallbackHandler.java
 *
 * This file was auto-generated from WSDL
 * by the Apache Axis2 version: 1.4.1  Built on : Aug 13, 2008 (05:03:35 LKT)
 */

    package mx.com.fact.www.schema.ws;

    /**
     *  FactWSFrontCallbackHandler Callback class, Users can extend this class and implement
     *  their own receiveResult and receiveError methods.
     */
    public abstract class FactWSFrontCallbackHandler{



    protected Object clientData;

    /**
    * User can pass in any object that needs to be accessed once the NonBlocking
    * Web service call is finished and appropriate method of this CallBack is called.
    * @param clientData Object mechanism by which the user can pass in user data
    * that will be avilable at the time this callback is called.
    */
    public FactWSFrontCallbackHandler(Object clientData){
        this.clientData = clientData;
    }

    /**
    * Please use this constructor if you don't want to set any clientData
    */
    public FactWSFrontCallbackHandler(){
        this.clientData = null;
    }

    /**
     * Get the client data
     */

     public Object getClientData() {
        return clientData;
     }

        
           /**
            * auto generated Axis2 call back method for RequestTransaction method
            * override this method for handling normal response from RequestTransaction operation
            */
           public void receiveResultRequestTransaction(
                    mx.com.fact.www.schema.ws.FactWSFrontStub.RequestTransactionResponse result
                        ) {
           }

          /**
           * auto generated Axis2 Error handler
           * override this method for handling error response from RequestTransaction operation
           */
            public void receiveErrorRequestTransaction(java.lang.Exception e) {
            }
                
           /**
            * auto generated Axis2 call back method for SSLTransaction method
            * override this method for handling normal response from SSLTransaction operation
            */
           public void receiveResultSSLTransaction(
                    mx.com.fact.www.schema.ws.FactWSFrontStub.SSLTransactionResponse result
                        ) {
           }

          /**
           * auto generated Axis2 Error handler
           * override this method for handling error response from SSLTransaction operation
           */
            public void receiveErrorSSLTransaction(java.lang.Exception e) {
            }
                
           /**
            * auto generated Axis2 call back method for MySuiteTransaction method
            * override this method for handling normal response from MySuiteTransaction operation
            */
           public void receiveResultMySuiteTransaction(
                    mx.com.fact.www.schema.ws.FactWSFrontStub.MySuiteTransactionResponse result
                        ) {
           }

          /**
           * auto generated Axis2 Error handler
           * override this method for handling error response from MySuiteTransaction operation
           */
            public void receiveErrorMySuiteTransaction(java.lang.Exception e) {
            }
                
           /**
            * auto generated Axis2 call back method for SecureTransaction method
            * override this method for handling normal response from SecureTransaction operation
            */
           public void receiveResultSecureTransaction(
                    mx.com.fact.www.schema.ws.FactWSFrontStub.SecureTransactionResponse result
                        ) {
           }

          /**
           * auto generated Axis2 Error handler
           * override this method for handling error response from SecureTransaction operation
           */
            public void receiveErrorSecureTransaction(java.lang.Exception e) {
            }
                
           /**
            * auto generated Axis2 call back method for ServiceCall method
            * override this method for handling normal response from ServiceCall operation
            */
           public void receiveResultServiceCall(
                    mx.com.fact.www.schema.ws.FactWSFrontStub.ServiceCallResponse result
                        ) {
           }

          /**
           * auto generated Axis2 Error handler
           * override this method for handling error response from ServiceCall operation
           */
            public void receiveErrorServiceCall(java.lang.Exception e) {
            }
                


    }
    