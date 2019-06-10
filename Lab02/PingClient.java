import java.io.*;
import java.net.*;
import java.util.*;

public class PingClient {
    private static final int TIMEUP = 1000; //1 second
    
    public static void main (String args[]) throws Exception{
    
        //1. Check and initialise arguments
        if(args.length < 2){
            System.out.println("Please enter arguments for host and port");
            return;
        }
        
        //Host server to connect to
        InetAddress hostServer;
        hostServer = InetAddress.getByName(args[0]);
        
        //Which port number to listen to
        int port = Integer.parseInt(args[1]);
        
        //Create a datagram socket to send and receive UDP packets
        DatagramSocket socket = new DatagramSocket();
        
        for (int num=0; num<10; num++){
            //Get the current time
            Date time = new Date();
            long timeSent = time.getTime();
            
            //String to send:
            String toSend = "PING "+num+" "+timeSent+" \r\n";
            //Convert to byte array
            byte[] buffer = new byte[1024];
            buffer = toSend.getBytes();
            
            //Create and send the data packet to the server
            DatagramPacket ping = new DatagramPacket(buffer, buffer.length, hostServer, port);
            socket.send(ping);
            
            //Check timeout value for packets
            try{
                socket.setSoTimeout(TIMEUP);
                
                //Create datagram packet
                DatagramPacket response = new DatagramPacket(new byte[1024], 1024);
                socket.receive(response);
                
                //Get timestamp for the time received
                time = new Date();
                long timeReceived = time.getTime();
                
                long delay = timeReceived-timeSent;
                
                //Print packet deets and delay
                printPacketData(response, num, delay);
            }catch(IOException e){
                //Packet has timed out!
                System.out.println("Packet #"+num+" has timed out!");
            }   
        }
        socket.close();
    }
    
    
    private static void printPacketData(DatagramPacket request, int num, long delayTime) throws Exception{
        byte[] buf = request.getData();
        //Wrap in input stream and readers
        ByteArrayInputStream bais = new ByteArrayInputStream(buf);
		InputStreamReader isr = new InputStreamReader(bais);
		
		BufferedReader br = new BufferedReader(isr);
		
		// Read output and save to string
		String output = br.readLine();
		
		// Print host address and data received from it.
		System.out.println(
		"ping to " + 
		request.getAddress().getHostAddress() + ": " +
		new String(output) + "\n" +
		"seq = " + num +
		", rtt = " + delayTime + " ms");
	}    

}
