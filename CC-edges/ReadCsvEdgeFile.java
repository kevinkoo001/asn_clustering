package cc_Lable;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

public class ReadCsvEdgeFile {
	public static void main(String[] args) {
		String readFilePath = "/Users/FM/desktop/cc-edge";
		File folder = new File(readFilePath);
		File[] files = folder.listFiles();
		for (File file: files) {
			boolean firstLine = true;
			String csvFile = file.getAbsolutePath();
			if (csvFile.equals("/Users/FM/desktop/cc-edge/.DS_Store"))
				continue;
			
			String [] pathParts = csvFile.split("/");
			//  /Users/FM/desktop/cc-edge/USA_edge.csv
			String [] lastPart = pathParts[pathParts.length - 1].split("_");
			String CC =  lastPart[0];
			BufferedReader br = null;
			String line = "";
			String cvsSplitBy = ",";
			String outputFile = "";
			try {
				br = new BufferedReader(new FileReader(csvFile));
				while ((line = br.readLine()) != null) {
					String[] row = line.split(cvsSplitBy);
					if (firstLine) {
						firstLine = false;
						outputFile += (row[0] + "," + row[1] + "," + row[2] + "\n");
//						outputFile += (row[0] + "," + row[1] + "\n");
					}
					else {
						outputFile += (row[0] + "," + row[1] + "," + row[2] + "\n");
//						outputFile += (row[0] + "," + row[1] + "\n");
					}

				}
				
				BufferedWriter bw = null;
				try {
			  		File writeFile = new File("/Users/FM/desktop/CC-edge-result/" + CC + "_edges.csv" );
			  		if (!writeFile.exists()) {
						writeFile.createNewFile();
					}
			  		FileWriter fw = new FileWriter(writeFile.getAbsoluteFile());
			  		bw = new BufferedWriter(fw);
			  		bw.write(outputFile);
			  		
		  		}catch (IOException e) {
					e.printStackTrace();
				} finally {
					if (bw != null)
						bw.close();
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
	
}
