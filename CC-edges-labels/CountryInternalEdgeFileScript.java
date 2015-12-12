import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class Main {
	public static void main(String[] args) {
		File mainDirectory = new File ("/home/fahimeh/Projects/CSE-592/asn_clustering/CC-edges-labels/data/");
		File[] allFiles = mainDirectory.listFiles();
		for (File theFile: allFiles) {
			String edgeFileName = theFile.getName();
			if (edgeFileName.contains("edge")) {
				
				String [] fileNameParts = edgeFileName.split("_");
				String countryName = fileNameParts[0];
				
				List<String> internalNodes = getInternalNodes(theFile.getAbsolutePath().replace("_edge", "_label"), countryName);
				
				
				List<String> internalEdges = new ArrayList<String>();
				internalEdges.add("Source,Target");
				
				BufferedReader br = null;
				String line = "";
				String cvsSplitBy = ",";

				try {

					br = new BufferedReader(new FileReader(theFile));
					while ((line = br.readLine()) != null) {

					        // use comma as separator
						String[] rowComponent = line.split(cvsSplitBy);
						if (internalNodes.contains(rowComponent[0]) && internalNodes.contains(rowComponent[1])) {
							internalEdges.add(line);
						}

					}

				} catch (FileNotFoundException e) {
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
				
				
				
				
				try
				{
					File file = new File ("/home/fahimeh/Projects/CSE-592/asn_clustering/CC-edges-labels/data_internal/" + edgeFileName);
					file.createNewFile();
				    FileWriter writer = new FileWriter("/home/fahimeh/Projects/CSE-592/asn_clustering/CC-edges-labels/data_internal/" + edgeFileName);
					for (String internalEdge: internalEdges) {
						writer.append(internalEdge);
						writer.append('\n');
					}
						
				    //generate whatever data you want
						
				    writer.flush();
				    writer.close();
				}
				catch(IOException e)
				{
				     e.printStackTrace();
				}
				
				
				
				
			}
		}
		
	}
	
	public static List<String> getInternalNodes(String labelFileName, String countryName) {
		System.out.println("labelFileName is " + labelFileName);
		List<String> result = new ArrayList<String>();
		
		
		BufferedReader br = null;
		String line = "";
		String cvsSplitBy = ",";

		try {
			File newFile = new File(labelFileName);
			if (newFile.exists()) {
				System.out.println("The File does exists !!");
			} else {
				System.out.println("The File does NOT exist !!");
			}
			br = new BufferedReader(new FileReader(labelFileName));
			while ((line = br.readLine()) != null) {

			        // use comma as separator
				String[] rowComponent = line.split(cvsSplitBy);
				if (rowComponent[1].equals(countryName)) {
					result.add(rowComponent[0]);
				}

			}

		} catch (FileNotFoundException e) {
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
		
		return result;
	}
}
