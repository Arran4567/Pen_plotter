package sample.controllers;

import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Alert;
import javafx.scene.control.TextField;
import javafx.scene.control.PasswordField;
import javafx.scene.layout.GridPane;
import javafx.stage.Stage;

public class Main {
    @FXML private TextField Username;
    @FXML private PasswordField Password;
    @FXML private GridPane ap;

    @FXML
    public void handleSubmitButtonAction(ActionEvent actionEvent) {
        if (Username.getText().toLowerCase().equals("admin") && Password.getText().equals("password")) {
            System.out.println("Correct!");
            try {
                FXMLLoader fxmlLoader = new FXMLLoader(getClass().getResource("../fxml/home.fxml"));
                Parent root1 = (Parent) fxmlLoader.load();
                Stage stage = new Stage();
                stage.setScene(new Scene(root1));
                stage.show();
                stage = (Stage) ap.getScene().getWindow();
                // do what you have to do
                stage.close();
            } catch(Exception e) {
                e.printStackTrace();
            }
        } else {
            Password.clear();
            Alert alert = new Alert(Alert.AlertType.ERROR);
            alert.setTitle("Incorrect!");
            alert.setHeaderText(null);
            alert.setContentText("Username or Password incorrect.\nPlease try again.");
            alert.showAndWait();
        }
    }
}
