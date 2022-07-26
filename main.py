from filecmp import clear_cache
from selenium import webdriver
import chromedriver_autoinstaller
from flask import Flask, render_template, request, redirect, send_file
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from urllib3.exceptions import NewConnectionError, MaxRetryError
import time
import csv
import pandas

chromedriver_autoinstaller.install()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-running-insecure-content')


file_path = None
file_name = None

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    global file_name
    global file_path
    error = None
    if request.method == "POST":      
        business = request.form["business"]
        area = request.form["area"]
        type = request.form["type"]

        if type == "All / Todo":
            file_type = "all"
        elif type == "Claimed / Reclamado":
            file_type = "claimed"
        elif type == "Unclaimed / No Reclamado":
            file_type = "unclaimed"

        file_path = f"./static/{business}_{area}_{file_type}.csv"
        file_name = f"{business}_{area}_{file_type}.csv"

        all_results = []
        parsed_results = []
        claimed_results = []
        unclaimed_results = []

        with open(file_path, 'w+', encoding="utf-8") as file:
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
                        
            scroll()

            failed_i = 0
            while True:
                try:
                    results = driver.find_elements_by_class_name("hfpxzc")
                    for result in results:
                     
                        if result in all_results:
                            continue
                            

                        name = result.get_attribute("aria-label")
                        result.send_keys(Keys.RETURN)
                        # try:
                        time.sleep(2)
                        # except IndexError:
                        #     time.sleep(3.5)
                        
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
                                    try:
                                        phone = driver.find_elements_by_class_name('Io6YTe')[-4]                                  
                                        is_number = int(phone.text[0])
                                    except:
                                        phone = driver.find_elements_by_class_name('Io6YTe')[-5] 


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

                        def append_full_results():
                            print(name)
                            print(phone.text)
                            all_results.append(result)
                            parsed_results.append([name, phone.text])

                        # if len(parsed_results) != 0:
                        #     for p_res in parsed_results:

                        #         if phone.text in p_res:
                        #             print(f"repeated results {phone.text}, {p_res[0]}")
                        #             break
                        #         else:
                        #             append_full_results()
                        # else:
                        #     append_full_results()

                        index = len(parsed_results) - 1

                        if index >= 0:
                            if phone.text == parsed_results[index][1]:
                                print(f"repeated results {phone.text}, repeated: {name}, original: {parsed_results[index][0]}")
                                continue
                            else:
                                append_full_results()
                        else:
                            append_full_results()
                            
                    
                    next = driver.find_element_by_xpath('//*[@id="eY4Fjd"]')
                    next.send_keys(Keys.RETURN)
                    time.sleep(3)
                    print("NEXT PAGE-----------------------------")

                except NoSuchElementException as e:
                    print(e)

                    scroll()

                    failed_i += 1

                    if failed_i == 15:
                        break

            driver.quit()
            print(f"All results:\n{all_results}")
            print(f"Claimed results:\n{claimed_results}")
            print(f"Unclaimed results:\n{unclaimed_results}")

        except Exception as e: 
            driver.quit()
            error = "Something Went Wrong :("
            print(e)

        with open(file_path, "a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
            
                if type == "All / Todo":
                    
                    writer.writerows(parsed_results)
                

                elif type == "Claimed / Reclamado":

                    writer.writerows(claimed_results)

                elif type == "Unclaimed / No Reclamado": 

                    writer.writerows(unclaimed_results)

        return redirect("/results") 
    
    return render_template("index.html", error=error)

@app.route("/results", methods=["GET", "POST"])
def search():

    if file_path == None:
        return redirect("/")

    # pd_data = pandas.read_csv(file_path)
    # result = pd_data.to_html(index=False)

    result = []
    with open(file_path) as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            result.append(row)

    return render_template("results.html", file = file_path, results = result)

@app.route("/download")
def download():
    return send_file(file_path, as_attachment=True, cache_timeout=0)

if __name__ == "__main__":
    app.run(debug=True)

