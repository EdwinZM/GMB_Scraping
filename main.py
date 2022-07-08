from selenium import webdriver
import chromedriver_autoinstaller
from flask import Flask, render_template, request, redirect
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time

chromedriver_autoinstaller.install()

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")



app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    error = None
    if request.method == "POST":
        business = request.form["business"]
        area = request.form["area"]
        type = request.form["type"]
        
        try:
            driver = webdriver.Chrome(options=chrome_options)

            driver.get("https://www.google.com/maps")
            
            searchbox = driver.find_element_by_id("searchboxinput")
            searchbox.send_keys(f"{business} {area}")
            searchbox.send_keys(Keys.RETURN)

            time.sleep(5)
            driver.quit()
        except Exception as e: 
            driver.quit()
            error = "Something Went Wrong :("
            print(e)
    
    return render_template("index.html", error=error)

@app.route("/results", methods=["GET", "POST"])
def search():

    return render_template("results.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)

