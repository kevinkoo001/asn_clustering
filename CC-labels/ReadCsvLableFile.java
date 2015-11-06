package cc_Lable;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

public class ReadCsvLableFile {
	public static void main(String[] args) {
		String csvFile = "/Users/FM/desktop/asn_reg-cymru.txt";
		BufferedReader br = null;
		String line = "";
		String cvsSplitBy = "|";
		Map<String, ArrayList<String>> countryASMap = new HashMap<String, ArrayList<String>>();

		try {
			br = new BufferedReader(new FileReader(csvFile));
			while ((line = br.readLine()) != null) {
				String[] partsOfLine = line.split("\\|");
				String CC = partsOfLine[1].trim();
				String ASName = partsOfLine[4].trim();
				String AS = partsOfLine[0].trim();
				String[] ASNameParts = ASName.split(",");
				
				if (CC.equals("ZZ")) {
				  	if (ASNameParts.length > 1 && 
				  			!ASNameParts[ASNameParts.length - 1].trim().equals("ZZ") &&
				  			ASNameParts[ASNameParts.length - 1].trim().length() == 2) {
				  		CC = ASNameParts[ASNameParts.length - 1].trim();
				  		if (countryASMap.containsKey(CC)) {
							ArrayList<String> asValues = countryASMap.get(CC);
							asValues.add(AS);
						} else {
							ArrayList<String> newASValues = new ArrayList<String>();
							countryASMap.put(CC, newASValues);
						}
				  	}	  	
				}
				else if (CC.equals(""))  {
					if (ASNameParts.length > 1 && 
							!ASNameParts[ASNameParts.length - 1].trim().equals("ZZ") &&
							ASNameParts[ASNameParts.length - 1].trim().length() == 2) {
						
				  		CC = ASNameParts[ASNameParts.length - 1].trim();
				  		if (countryASMap.containsKey(CC)) {
							ArrayList<String> asValues = countryASMap.get(CC);
							asValues.add(AS);
						} else {
							ArrayList<String> newASValues = new ArrayList<String>();
							countryASMap.put(CC, newASValues);
						}
				  	}
				}
				else {
				  	String [] ASNameParts2 = ASName.split(",");
				  	String CCInASName = (ASNameParts2[ASNameParts2.length - 1]);
				  	if (ASNameParts2.length > 1 && CCInASName.length() == 2)
					  	if (!CC.equals(CCInASName) && !CCInASName.equals("ZZ"))
					  		CC = CCInASName;
					
					if (countryASMap.containsKey(CC)) {
						ArrayList<String> asValues = countryASMap.get(CC);
						asValues.add(AS);
					} else {
						ArrayList<String> newASValues = new ArrayList<String>();
						countryASMap.put(CC, newASValues);
					}
				}
			}
			
			Iterator it = countryASMap.entrySet().iterator();
			while (it.hasNext()) {
				Map.Entry pair = (Map.Entry)it.next();
				String CC = (String) pair.getKey();
				ArrayList<String> ASs = (ArrayList<String>) pair.getValue();
				
		  		BufferedWriter bw = null;
		  		try {
			  		File file = new File("/Users/FM/desktop/CC-labels/" + CC + "_label.csv" );
			  		if (!file.exists()) {
						file.createNewFile();
					}
			  		FileWriter fw = new FileWriter(file.getAbsoluteFile());
			  		bw = new BufferedWriter(fw);
			  		for (String AS: ASs) 
			  			bw.write(AS + "," + CC + "\n");
			  		
		  		}catch (IOException e) {
					e.printStackTrace();
				} finally {
					if (bw != null)
						bw.close();
				}
			}
			
		}catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			if (br != null) {
				try {
					br.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}
	}
}