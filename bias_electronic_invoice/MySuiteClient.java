import edu.mscd.cs.jclo.JCLO;
import mx.com.fact.www.schema.ws.*;
import mx.com.fact.www.schema.ws.FactWSFrontStub.*;
import java.io.*;
import org.apache.axis2.transport.http.HTTPConstants;
import org.apache.axis2.client.Options;


class ReadTextFile {

    /**
     * Fetch the entire contents of a text file, and return it in a String.
     * This style of implementation does not throw Exceptions to the caller.
     *
     * @param aFile is a file which already exists and can be read.
     */
    static public String getContents(String fname) {
	File aFile = new File(fname);
	//...checks on aFile are elided
	StringBuilder contents = new StringBuilder();
	
	try {
	    //use buffering, reading one line at a time
	    //FileReader always assumes default encoding is OK!
	    BufferedReader input =  new BufferedReader(new FileReader(aFile));
	    try {
		String line = null; //not declared within while loop
		/*
		 * readLine is a bit quirky :
		 * it returns the content of a line MINUS the newline.
		 * it returns null only for the END of the stream.
		 * it returns an empty String if two newlines appear in a row.
		 */
		while (( line = input.readLine()) != null){
		    contents.append(line);
		    contents.append(System.getProperty("line.separator"));
		}
	    }
	    finally {
		input.close();
	    }
	}
	catch (IOException ex){
	    ex.printStackTrace();
	}
	return contents.toString();
    }
}


class Argumentos {
    public String requestor = "";
    public String transaction = "";
    public String country = "";
    public String entity = "";
    public String user = "";
    public String username = "";
    public String data1 = "";
    public String data2 = "";
    public String data3 = "";
}


public class MySuiteClient {

    private RequestTransaction getBasicParam(Argumentos aa) {
	RequestTransaction param = new RequestTransaction();
	param.setRequestor(aa.requestor);
	param.setCountry(aa.country);
	param.setEntity(aa.entity);
	param.setUser(aa.user);
	param.setUserName(aa.username);
	return param;
    }

    private TransactionTag doTransaction(RequestTransaction param) throws Exception {
	FactWSFrontStub stub = new FactWSFrontStub();
	RequestTransactionResponse resp = stub.RequestTransaction(param);
	TransactionTag tag = resp.getRequestTransactionResult();
	return tag;
    }

    private void showResults(TransactionTag tag) {
	FactResponse fact = tag.getResponse();
	FactResponseData data = tag.getResponseData();
	if (fact.getResult())
	    System.out.println("Resultado ok.");
	else
	    System.out.println("Resultado ERRONEO.");
	System.out.println("Hint: " + fact.getHint());
	System.out.println("Data: " + fact.getData());
	System.out.println("Respuesta: " + fact.getDescription());
	System.out.println("Data1: " + data.getResponseData1());
	System.out.println("Data2: " + data.getResponseData2());
	System.out.println("Data3: " + data.getResponseData3());
    }

    private void ConvertNative(Argumentos aa) throws Exception {
	RequestTransaction param = getBasicParam(aa);
	ReadTextFile fid = new ReadTextFile();
	String data1 = fid.getContents(aa.data1);
	param.setTransaction("CONVERT_NATIVE_XML");
	param.setData1(data1);
	param.setData2(aa.data2);
	param.setData3(aa.data3);
	TransactionTag tag = doTransaction(param);
	showResults(tag);
    }

    public void Generico(Argumentos aa) throws Exception {
	RequestTransaction param = getBasicParam(aa);
	param.setTransaction(aa.transaction);
	param.setData1(aa.data1);
	param.setData2(aa.data2);
	param.setData3(aa.data3);
	TransactionTag tag = doTransaction(param);
	showResults(tag);
    }

    public static void main(String args[]) throws Exception {
	Options options = new Options();
	options.setProperty(HTTPConstants.SO_TIMEOUT, new Integer(100000));  // timeout in milliseconds
	options.setProperty(HTTPConstants.CONNECTION_TIMEOUT, new Integer(100000));  // timeout in milliseconds
	// options.setTimeOutInMilliSeconds(100000); 
	MySuiteClient cc = new MySuiteClient();
	Argumentos aa = new Argumentos();
	JCLO jclo = new JCLO(aa);
	jclo.parse(args);
	if (aa.transaction.equals("CONVERT_NATIVE_XML"))
	    cc.ConvertNative(aa);
	else
	    cc.Generico(aa);
    }
}

