# Pneumonia AI Detection

This project is an AI-based Pneumonia detection system designed to classify chest X-ray images into categories such as **Normal**, **Pneumonia** using a pre-trained model. The system provides a web-based interface where users can upload chest X-ray images, and the model will classify them with a confidence level for each category. 

The model used in this system is a pre-trained VGG model that has been fine-tuned for pneumonia detection. The web application is built using **Flask** and **TensorFlow**.

## Features
- **Image Classification**: Classifies chest X-ray images into **Normal**, **Bacterial Pneumonia**, and **Viral Pneumonia** categories.
- **Web Interface**: Users can upload chest X-ray images through a simple web interface and view the classification results.
- **Confidence Scoring**: Provides a confidence score for each classification category.
- **Database**: Stores patient information and their respective classification results in an SQLite database.

## Project Overview
The Pneumonia AI Detection project aims to build a machine learning model that can classify chest X-ray images to help healthcare professionals identify pneumonia in patients. The model leverages a Convolutional Neural Network (CNN) architecture, specifically a VGG model, to predict the likelihood of pneumonia in the uploaded images. 

This project can assist in providing a quick diagnostic tool for healthcare facilities, especially in regions where access to doctors or radiologists is limited.

### Technologies Used:
- **Flask**: A Python web framework used to build the web application.
- **TensorFlow**: An open-source machine learning framework to train and run the model.
- **SQLite**: A lightweight database to store user and prediction information.
- **Git Large File Storage (LFS)**: To manage large model files.
- **HTML/CSS/JavaScript**: For building the front-end user interface.

## Setup Instructions

### 1. Clone the Repository:
Clone the project repository to your local machine:

```bash
git clone https://github.com/Sidddhh/Pneumonia_Ai.git
cd Pneumonia_Ai
