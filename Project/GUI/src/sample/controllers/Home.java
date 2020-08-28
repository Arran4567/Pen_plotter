package sample.controllers;

import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.TextField;
import javafx.scene.image.Image;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import javafx.scene.image.ImageView;

import javax.imageio.ImageIO;
import java.awt.*;
import java.io.File;
import java.net.URL;

public class Home {
    @FXML private TextField filePath;
    @FXML private ImageView imageView;

    public void handleFileSearchButton(ActionEvent actionEvent) {
        FXMLLoader fxmlLoader = new FXMLLoader(getClass().getResource("../fxml/home.fxml"));
        try{
            Parent root1 = (Parent) fxmlLoader.load();
            Stage stage = new Stage();
            stage.setScene(new Scene(root1));
            FileChooser fileChooser = new FileChooser();
            fileChooser.setTitle("Open Resource File");
            fileChooser.getExtensionFilters().addAll(
                    new FileChooser.ExtensionFilter("IMAGE FILES", "*.jpg", "*.png"),
                    new FileChooser.ExtensionFilter("DXF", "*.dxf")
            );
            File file = fileChooser.showOpenDialog(stage);
            if (file != null) {
                filePath.setText(file.getPath());
            } else  {
                System.out.println("No File selected."); // or something else
            }
            if(filePath.getText().endsWith(".png") || filePath.getText().endsWith(".jpg")) {
                Image img = new Image(file.toURI().toString());
                imageView.setImage(img);
            } else if(filePath.getText().endsWith(".dxf")){
                //Get preview of dxf

            } else{
                System.out.println("Unknown File Type.");
            }
        }catch(Exception e){
            e.printStackTrace();
        }

    }

    public void handleCalibrateButton(ActionEvent actionEvent) {
        
    }
}
