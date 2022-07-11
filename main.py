from selenium import webdriver
import chromedriver_autoinstaller
from flask import Flask, render_template, request, redirect
from selenium.webdriver.common.keys import Keys
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

            time.sleep(3)

            # driver.execute_script("var el = document.evaluate('/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; el.scroll(0, 5000);")

            body = driver.find_element_by_xpath('/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]')
            for i in range(10):
                body.send_keys(Keys.PAGE_DOWN)


            time.sleep(3)

            results = driver.find_elements_by_class_name("hfpxzc")

            for result in results:
                print(result.get_attribute("aria-label"))
                result.send_keys(Keys.RETURN)
                time.sleep(2)
                
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
    app.run(debug=True)

