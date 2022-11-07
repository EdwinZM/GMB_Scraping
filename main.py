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

                        neg_ind = -2
                        num_ind = 0
                        max_rec = 0
                        phone = None

                        def get_info(neg, num, max_rec):
                                try:
                                    phone = driver.find_elements_by_class_name('Io6YTe')[neg]
                                    is_number = int(phone.text[num])
                                    # claimed_results.append([name, phone.text])

                                    claiming_btn = driver.find_elements_by_class_name('Io6YTe')[-1]
                                    claim_txt = claiming_btn.text

                                    if claim_txt.lower() == "claim this business" or claim_txt.lower() == "reclamar este negocio":
                                        print("up to claim")
                                        unclaimed_results.append([name, phone.text])
                                    else:
                                        claimed_results.append([name, phone.text])
                                

                                except:
                                    neg -= 1
                                    num += 1
                                    max_rec += 1

                                    if max_rec >= 10:
                                        error = "Unable to find phone number :("
                                        return error
                                    else:
                                        get_info(neg, num, max_rec)
                        get_info(neg_ind, num_ind, max_rec)

                        def append_full_results():
                            
                            cindex = len(claimed_results) - 1
                            uindex = len(unclaimed_results) - 1
                            print(cindex)
                            print(uindex)

                            def loop_results(i, res, p_results, a_results, r):
                                if i >= 0:
                                    if res[i] not in p_results:
                                        p_results.append(res[i])
                                        print(res[i][1])
                                        a_results.append(r)
                                    else:
                                        print(f"{res[i]} repeated")
                                        res.remove(res[i])
                            
                            loop_results(cindex, claimed_results, parsed_results, all_results, result)
                            loop_results(uindex, unclaimed_results, parsed_results, all_results, result)
                                        
                                
                                    

                            
                                        #parsed_results.append([name, phone.text])
                        append_full_results()
                       
                    
                    next = driver.find_element_by_xpath('//*[@id="eY4Fjd"]')
                    next.send_keys(Keys.RETURN)
                    time.sleep(3)
                    print("NEXT PAGE-----------------------------")
                    failed_i = 0

                except NoSuchElementException as e:
                    print(e)

                    scroll()

                    failed_i += 1
                    print(f"failed_i: {failed_i}")

                    if failed_i == 10: #15
                        break
                else:
                    failed_i = 0

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

