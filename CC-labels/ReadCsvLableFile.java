package cc_Lable;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

public class ReadCsvLableFile {
	public static void main(String[] args) {
		String csvFile = "/Users/FM/desktop/asn_reg-cymru.txt";
		BufferedReader br = null;
		String line = "";
		String cvsSplitBy = "|";

		try {
			br = new BufferedReader(new FileReader(csvFile));
			while ((line = br.readLine()) != null) {
				String[] partsOfLine = line.split("\\|");
				String CC = partsOfLine[1].trim();
				String ASName = partsOfLine[4].trim();
				String AS = partsOfLine[0].trim();
				String[] ASNameParts = ASName.split(",");
				if (CC.equals("ZZ")) {
				  	if (!ASNameParts[ASNameParts.length - 1].trim().equals("ZZ")) {
				  		CC = ASNameParts[ASNameParts.length - 1].trim();
				  		BufferedWriter bw = null;
				  		try {
					  		File file = new File("/Users/FM/desktop/CC-labels/" + CC + "_label.csv" );
					  		if (!file.exists()) {
								file.createNewFile();
							}
					  		FileWriter fw = new FileWriter(file.getAbsoluteFile());
					  		bw = new BufferedWriter(fw);
					  		bw.write(AS + "," + CC + "\n");
					  		
				  		}catch (IOException e) {
							e.printStackTrace();
						} finally {
							if (bw != null)
								bw.close();
						}
				  	}
				}
				else {
					BufferedWriter bw = null;
					try {
				  		File file = new File("/Users/FM/desktop/CC-labels/" + CC + "_label.csv" );
				  		if (!file.exists()) {
							file.createNewFile();
						}
				  		FileWriter fw = new FileWriter(file.getAbsoluteFile());
				  		bw = new BufferedWriter(fw);
				  		String [] ASNameParts2 = ASName.split(",");
				  		String CCInASName = (ASNameParts2[ASNameParts2.length - 1]);
				  		if (!CC.equals(CCInASName))
				  			bw.write(AS + "," + CCInASName + "\n");
				  		else
				  			bw.write(AS + "," + CC + "\n");
				  		
			  		}catch (IOException e) {
						e.printStackTrace();
					} finally {
						if (bw != null)
							bw.close();
					}
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