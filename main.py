from selenium import webdriver
import chromedriver_autoinstaller
from flask import Flask, render_template, request, redirect
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from urllib3.exceptions import NewConnectionError, MaxRetryError
import time
import csv

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

        all_results = []
        parsed_results = []
        claimed_results = []
        unclaimed_results = []

        with open("./static/results.csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(["name", " phone"])
        
        try:
            driver = webdriver.Chrome(options=chrome_options)

            driver.get("https://www.google.com/maps")
            
            searchbox = driver.find_element_by_id("searchboxinput")
            searchbox.send_keys(f"{business} {area}")
            searchbox.send_keys(Keys.RETURN)

            time.sleep(4)


            body = driver.find_element_by_xpath('/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]')
            
            def scroll():
                for i in range(10):
                    body.send_keys(Keys.PAGE_DOWN)
                        
            # time.sleep(2)
            scroll()

            failed_i = 0
            while True:
                try:
                    results = driver.find_elements_by_class_name("hfpxzc")
                    for result in results:
                     
                        if result in all_results:
                            continue
                            

                        name = result.get_attribute("aria-label")
                        print(name)
                        result.send_keys(Keys.RETURN)
                        try:
                            time.sleep(2)
                        except IndexError:
                            time.sleep(3.5)
                        
                        try:
                            try:
                                phone = driver.find_elements_by_class_name('Io6YTe')[-2]
                                is_number = int(phone.text[0])
                                claimed_results.append([name, phone.text])
                            except:

                                try:
                                    phone = driver.find_elements_by_class_name('Io6YTe')[-3]
                                    is_number = int(phone.text[0])
                                except: 
                                    # try:
                                        phone = driver.find_elements_by_class_name('Io6YTe')[-4]
                                    #     is_number = int(phone.text[0])
                                    # except:
                                    #     phone = driver.find_elements_by_class_name('Io6YTe')[-5]  

                                claiming_btn = driver.find_elements_by_class_name('Io6YTe')[-1]
                                claim_txt = claiming_btn.text
                                print(f"claiming text: {claim_txt}")

                                if claim_txt.lower() == "claim this business" or claim_txt.lower() == "reclamar este negocio":
                                    print("up to claim")
                                    unclaimed_results.append([name, phone.text])
                                else:
                                    claimed_results.append([name, phone.text])
                        except: 
                            continue

                        print(phone.text)
                        all_results.append(result)
                        parsed_results.append([name, phone.text])
                    
                    next = driver.find_element_by_xpath('//*[@id="eY4Fjd"]')
                    next.send_keys(Keys.RETURN)
                    time.sleep(3)
                    print("NEXT PAGE-----------------------------")

                except NoSuchElementException as e:
                    print(e)

                    scroll()

                    failed_i += 1

                    if failed_i == 10:
                        break
                # else:
                #     raise Exception
            driver.quit()
            print(f"All results:\n{all_results}")
            print(f"Claimed results:\n{claimed_results}")
            print(f"Unclaimed results:\n{unclaimed_results}")

           
        # except NewConnectionError as e:
        #     driver.quit()
        #     print(e)

        # except MaxRetryError as e:
        #     driver.quit()
        #     print(e)

        except Exception as e: 
            driver.quit()
            error = "Something Went Wrong :("
            print(e)

        with open("./static/results.csv", "a", newline="") as file:
            writer = csv.writer(file)
        
            if type == "All / Todo":
                # type_results = all_results


                
                writer.writerows(parsed_results)
               

            elif type == "Claimed / Reclamado":
                # type_results = claimed_results
                # for result in claimed_results:
                #     # file.write(f"{result[0]}, {result[1]}")
                #     writer.writerow(result)
                writer.writerows(claimed_results)

            elif type == "Unclaimed / No Reclamado": 
                # type_results = unclaimed_results
                # for result in unclaimed_results:
                #     file.write(f"{result[0]}, {result[1]}")
                #     # writer.writerow([result[0], result[1]])
                writer.writerows(unclaimed_results)


        return render_template("results.html")
    
    return render_template("index.html", error=error)

@app.route("/results", methods=["GET", "POST"])
def search():

    return render_template("results.html")

if __name__ == "__main__":
    app.run(debug=True)

