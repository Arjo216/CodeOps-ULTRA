import java.util.*;

class Main {
    public static void main(String[] args) {
        // A messy simulated server log
        String logData = "error:404,success:200,error:500,warning:199,success:200,error:404,error:500";
        String[] logs = logData.split(",");
        
        List<String> uniqueErrors = new ArrayList<String>();
        
        // TERRIBLE O(n^2) LOOP WITH BUGGY STRING COMPARISON
        for(int i = 0; i < logs.length; i++) {
            if(logs[i].contains("error")) {
                boolean isDuplicate = false;
                for(int j = 0; j < uniqueErrors.size(); j++) {
                    // CRITICAL BUG: Using == instead of .equals() for objects
                    if(uniqueErrors.get(j) == logs[i]) { 
                        isDuplicate = true; 
                    }
                }
                if(isDuplicate == false) { 
                    uniqueErrors.add(logs[i]); 
                }
            }
        }
        
        // TERRIBLE MEMORY MANAGEMENT (String concatenation in a loop)
        String output = "";
        for(int k = 0; k < uniqueErrors.size(); k++) { 
            output = output + uniqueErrors.get(k) + " | "; 
        }
        
        System.out.println("CRITICAL FAULTS FOUND: " + output);
    }
}