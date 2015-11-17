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
import java.util.HashSet;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;

public class CountryLabelFileScript {
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
			
			Set<String> assWithoutCountry = new HashSet<String>();
			
			File edgesFolder = new File("/Users/FM/desktop/CC-edge-result/");
			File[] countries = edgesFolder.listFiles();
//			Map <String, Set<String>> asInCountries = new HashMap<String, Set<String>>();
			for (File country: countries) {
				BufferedReader br2 = null;
				try {
					br2 = new BufferedReader(new FileReader(country.getAbsolutePath()));
//					System.out.println(country.getAbsolutePath());
					String lineInEdgeFile;
					String [] countryNameParts = country.getAbsolutePath().split("/");
					String [] lastPartOfFileName = countryNameParts[countryNameParts.length - 1].split("_");
					String countryName = lastPartOfFileName[0];
//					System.out.println(countryName);
					Set<String> assInSpecificCountry = new HashSet<String>();
					while ((lineInEdgeFile = br2.readLine()) != null) {
//						System.out.println(lineInEdgeFile);
						String[] AsParts = lineInEdgeFile.split(",");
						assInSpecificCountry.add(AsParts[0]);
						assInSpecificCountry.add(AsParts[1]);
					}
					
//					asInCountries.put(countryName, assInSpecificCountry);
					
					BufferedWriter bw = null;
			  		try {
				  		File file = new File("/Users/FM/desktop/CC-label-result/" + countryName + "_label.csv" );
				  		if (!file.exists()) {
							file.createNewFile();
						}
				  		FileWriter fw = new FileWriter(file.getAbsoluteFile());
				  		bw = new BufferedWriter(fw);
				  		
				  		for (String asInSpecificCountry: assInSpecificCountry) {
				  			String countryForSpecificAS = countryASMap.get(asInSpecificCountry);
				  			if (countryForSpecificAS == null)
				  				assWithoutCountry.add(asInSpecificCountry);
				  			
				  			String newLine = asInSpecificCountry + "," + countryForSpecificAS + "\n";
				  			bw.write(newLine);
				  		}
				  		
			  		}catch (IOException e) {
						e.printStackTrace();
					} finally {
						if (bw != null)
							bw.close();
					}
				} catch (FileNotFoundException e) {
					e.printStackTrace();
				} catch (IOException e) {
					e.printStackTrace();
				} finally {
					br2.close();
				}
				
			}
			
			System.out.println("The number of AS without assigned country is " + assWithoutCountry.size());
			System.out.println("The list of AS (without assigned country is): ");
			for (String aswithoutCountry: assWithoutCountry) {
				System.out.println(aswithoutCountry);
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
