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

public class CountryEdgeFileScript {
	public static void main(String[] args) {
		String csvFile = "/Users/FM/desktop/asn_reg-cymru.txt";
		BufferedReader br = null;
		String line = "";
		String cvsSplitBy = "|";
		Map<String, String> countryASMap = new HashMap<String, String>();

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
				  			ASNameParts[ASNameParts.length - 1].trim().length() == 2)
				  	{
				  		CC = ASNameParts[ASNameParts.length - 1].trim();
				  		countryASMap.put(AS, CC);
				  	}	  	
				}
				else if (CC.equals(""))  {
					if (ASNameParts.length > 1 && 
							!ASNameParts[ASNameParts.length - 1].trim().equals("ZZ") &&
							ASNameParts[ASNameParts.length - 1].trim().length() == 2) {
						
				  		CC = ASNameParts[ASNameParts.length - 1].trim();
				  		countryASMap.put(AS, CC);
				  	}
				}
				else {
				  	String [] ASNameParts2 = ASName.split(",");
				  	String CCInASName = (ASNameParts2[ASNameParts2.length - 1]);
				  	if (ASNameParts2.length > 1 && CCInASName.length() == 2)
					  	if (!CC.equals(CCInASName) && !CCInASName.equals("ZZ"))
					  		CC = CCInASName;
				  	countryASMap.put(AS, CC);
				}
			}
	
			Map<String, String> ultimate = new HashMap<String, String>();
			
			String caidaFile = "/Users/FM/desktop/caida.txt";
			BufferedReader br2 = null;
			String line2 = "";
			String splitString = "\\|";
			try {
				br2 = new BufferedReader(new FileReader(caidaFile));
				while ((line2 = br2.readLine()) != null) {
					String[] lineParts = line2.split(splitString);
					String sourceAS = lineParts[0].trim();
					String destinationAS = lineParts[1].trim();
					
					String country = countryASMap.get(sourceAS);
					if (country != null) {
						String outputFile = ultimate.get(country);
						if (outputFile != null) {
							String currentOutput = ultimate.get(country);
							currentOutput += "\n" + sourceAS + "," + destinationAS;
							ultimate.put(country, currentOutput);
						} else {
							ultimate.put(country, sourceAS + "," + destinationAS);
						}
					} else
						System.err.println("for sourceAS " + sourceAS + ", the country doesn't exist !!!!");
		
				}
			} catch(IOException e) {
				e.printStackTrace();
			} finally {
				br2.close();
			}
		
			Iterator it = ultimate.entrySet().iterator();
			while (it.hasNext()) {
				Map.Entry pair = (Map.Entry)it.next();
				String CC = (String) pair.getKey();
				String ASinfo = (String) pair.getValue();
				
		  		BufferedWriter bw = null;
		  		try {
			  		File file = new File("/Users/FM/desktop/CC-edge-result/" + CC + "_edge.csv" );
			  		if (!file.exists()) {
						file.createNewFile();
					}
			  		FileWriter fw = new FileWriter(file.getAbsoluteFile());
			  		bw = new BufferedWriter(fw);
			  		bw.write(ASinfo);
			  		
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
