// https://github.com/gephi/gephi/tree/master/modules/StatisticsPlugin/src/main/java/org/gephi/statistics/plugin
// https://github.com/gephi/gephi/tree/master/modules/StatisticsPlugin/src/main/java/org/gephi/statistics/plugin


/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package org.gephi.statistics.plugin;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.gephi.data.attributes.api.AttributeController;
import org.gephi.data.attributes.api.AttributeModel;
import org.gephi.graph.api.GraphController;
import org.gephi.graph.api.GraphModel;
import org.gephi.graph.api.UndirectedGraph;
import org.gephi.io.importer.api.Container;
import org.gephi.io.importer.api.EdgeDefault;
import org.gephi.io.importer.api.ImportController;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.project.api.ProjectController;
import org.gephi.project.api.Workspace;
import org.openide.util.Lookup;

/**
 *
 * @author fahimeh
 */
public class GephiToolKitTest {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        List<String> finalResult = new ArrayList<String>();
        finalResult.add("country, Average Degree, Diameter, Radius, Average Path Length, Graph Density, Modularity, "
                + "CommunityNumber, Connected Components, Averge Clustering Coefficient, Total Triangles\n");
        
        File mainDirectory = new File("/Users/FM/Desktop/CSE592/asn_clustering/CC-edges-labels/data_internal_2/");
        File[] files =  mainDirectory.listFiles();
        for (File file: files) {
        	if (file.getName().equals(".DS_Store"))
        		continue;
            GephiToolKitTest test = new GephiToolKitTest();
            String[] fileNameParts = file.getName().split("_"); 
            String countryName = fileNameParts[0];
            System.out.println(file.getAbsolutePath());
            finalResult.add(test.runTheExperiment(countryName, file.getAbsolutePath()));
        }
        
        
        try
    	{
        	File excelOutputFile = new File("/Users/FM/Desktop/CSE592/asn_clustering/CC-edges-labels/metrics.csv");
    	    FileWriter writer = new FileWriter("/Users/FM/Desktop/CSE592/asn_clustering/CC-edges-labels/metrics.csv");
    		
    	    for (String line: finalResult) {
    	    	writer.append(line);
    	    }
    	   	
    			
    	    writer.flush();
    	    writer.close();
    	}
    	catch(IOException e)
    	{
    	     e.printStackTrace();
    	} 
        
    }
    
    public String runTheExperiment(String countryName, String filePath) {
        
        String result = countryName + ", ";
        
        //Init a project - and therefore a workspace
        ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
        pc.newProject();
        Workspace workspace = pc.getCurrentWorkspace();

        //Get controllers and models
        ImportController importController = Lookup.getDefault().lookup(ImportController.class);
        GraphModel graphModel = Lookup.getDefault().lookup(GraphController.class).getModel();
        AttributeModel attributeModel = Lookup.getDefault().lookup(AttributeController.class).getModel();
        
        //Import file
        Container container;
        try {
            File file = new File(filePath);
            container = importController.importFile(file);
            container.getLoader().setEdgeDefault(EdgeDefault.UNDIRECTED);   //Force UNDIRECTED
            
        } catch (Exception ex) {
            ex.printStackTrace();
            return null;
        }

       
        importController.process(container, new DefaultProcessor(), workspace);
        UndirectedGraph graph = graphModel.getUndirectedGraph();
        Degree degree = new Degree();
        degree.execute(graph.getGraphModel(), attributeModel);
        // AVERAGE DEGREE
        System.out.println("Average Degree: " + degree.getAverageDegree()); // ==> [1] Average Degree
        result += (String.valueOf(degree.getAverageDegree())) + ", ";
        
        // NETWORK DIAMETER
        GraphDistance distance = new GraphDistance();
        distance.setDirected(false);
        distance.execute(graphModel, attributeModel);
        
        System.out.println("Diameter: " + distance.getDiameter()); // ==> [2] Diameter
        result += (String.valueOf(distance.getDiameter())) + ", ";
        
        String distanceReport = distance.getReport();
        int radiusIndex = distanceReport.indexOf("Radius:");
        String radiusPart = distanceReport.substring(radiusIndex);
        String[] parts2 = radiusPart.split(" ");
        String[] parts22 = parts2[1].split("<br");
        double radius = Double.parseDouble(parts22[0]);
        
        System.out.println("Radius: " + radius); // ==> [3] Radius
        result += (String.valueOf(radius)) + ", ";
        
        System.out.println("Average Path Length" + distance.getPathLength()); // ==> [4] Average Path Length
        result += (String.valueOf(distance.getPathLength())) + ", ";
        
        // TODO: Shortest Path
        
        // GRAPH DENSITY
        System.out.println("Graph Density: " +  calculateDensity(graph, false)); // ==> [5] Graph Density
        result += (String.valueOf(calculateDensity(graph, false))) + ", ";
        
        // MODULARITY
        Modularity mod = new Modularity();
        
        mod.execute(graphModel, attributeModel);
        String modularityReport = mod.getReport();
        int modularityIndex = modularityReport.indexOf("Modularity: ");
        String modularityReportSubString = modularityReport.substring(modularityIndex);
        String[] parts = modularityReportSubString.split("<br>");
        String[] modularityParts = parts[0].split(" ");
        double modularityValue =  Double.parseDouble(modularityParts[1]);
        
        System.out.println("Modularity Value is: " + modularityValue); // ==> [6] Modularity
        result += (String.valueOf(modularityValue)) + ", ";
        
        
//        System.out.println("OR modularity Value is (through function call): " + mod.getModularity());
        
        int communityIndex = modularityReport.indexOf("Number of Communities:");
        parts = modularityReport.substring(communityIndex).split("<br />");
        String[] communityParts = parts[0].split(" ");
        int communityNumber = Integer.parseInt(communityParts[3]);
        
        System.out.println("Communitiy Number is: " + communityNumber); // ==> [7] CommunityNumber
        result += (String.valueOf(communityNumber)) + ", ";
        
        
        //CONNECTED COMPONENTS
        ConnectedComponents connComp = new ConnectedComponents();
        connComp.execute(graphModel, attributeModel);
        
        System.out.println("Connected Components: " + connComp.getConnectedComponentsCount()); // [8] Connected Components
        result += (String.valueOf(connComp.getConnectedComponentsCount())) + ", ";
        
        // CLUSTERING COEFFICIENTS
        ClusteringCoefficient clustCoeff = new ClusteringCoefficient();
        clustCoeff.execute(graphModel, attributeModel);
        System.out.println("Average Clustering Coefficients: " + clustCoeff.getAverageClusteringCoefficient()); // ==> [9] Averge Clustering Coefficient
        result += (String.valueOf(clustCoeff.getAverageClusteringCoefficient())) + ", ";
        
        String clusterCoefficientResult = clustCoeff.getReport();
        int triangleIndex = clusterCoefficientResult.indexOf("Total triangles:");
        String[] triangleParts = clusterCoefficientResult.substring(triangleIndex).split(" ");
        String[] theValue = triangleParts[2].split("<br");
        System.out.println("Total Triangles: " + theValue[0]); // [10] Total Triangles
        result += (theValue[0]) + "\n";
        
        return result;
    }   
    
    
    
    // for calculating the graph density
    public double calculateDensity(UndirectedGraph graph, boolean isGraphDirected) {
        double result;

        double edgesCount = graph.getEdgeCount();
        double nodesCount = graph.getNodeCount();
        double multiplier = 1;

        if (!isGraphDirected) {
            multiplier = 2;
        }
        result = (multiplier * edgesCount) / (nodesCount * nodesCount - nodesCount);
        return result;
    }
    
    
}
