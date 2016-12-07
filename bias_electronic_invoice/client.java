import mx.com.fact.www.schema.ws.*;
import mx.com.fact.www.schema.ws.FactWSFrontStub.*;

public class client {

    public static void main(String args[]) throws Exception {
	FactWSFrontStub stub = new FactWSFrontStub();
	RequestTransaction param = new RequestTransaction();
	param.setRequestor("12511111-3411-1111-1111-111111321511");
	param.setTransaction("GET_DOCUMENT");
	param.setCountry("MX");
	param.setEntity("EUN040506RB3");
	param.setUser("12511111-3411-1111-1111-111111321511");
	param.setUserName("MX. EUN040506RB3.jacinto");
	param.setData1("E");
	param.setData2("101");
	param.setData3("PDF HTML");
	RequestTransactionResponse resp = stub.RequestTransaction(param);
	TransactionTag tag = resp.getRequestTransactionResult();
	FactResponse fact = tag.getResponse();
	if (fact.getResult())
	    System.out.println("Resultado ok.");
	else
	    System.out.println("Resultado ERRONEO.");
	System.out.println("Hint: " + fact.getHint());
	System.out.println("Data: " + fact.getData());
	System.out.println("Respuesta: " + fact.getDescription());
    }
}