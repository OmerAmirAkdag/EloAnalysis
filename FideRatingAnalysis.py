from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit,QPushButton, QHBoxLayout,QVBoxLayout,QApplication, QMessageBox,QTableWidget
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from collections import Counter



class Main(QWidget):
    
    def __init__(self):

        super(Main,self).__init__()
        self.setWindowTitle("Rating Analyzer")
        self.setFixedSize(400, 130)
        self.nameLabel = QLabel("Surname, Name : ")
        self.nameLineEdit = QLineEdit()
        self.applyButton = QPushButton("Apply")
        HBox = QHBoxLayout()
        
        HBox0 = QHBoxLayout()
        HBox0.addWidget(self.nameLabel)
        HBox0.addWidget(self.nameLineEdit)
        HBox1 = QHBoxLayout()
        HBox1.addStretch()
        HBox1.addWidget(self.applyButton)
        VBox0 = QVBoxLayout()
        VBox0.addLayout(HBox)
        VBox0.addLayout(HBox0)
        VBox0.addLayout(HBox1)

        self.setLayout(VBox0)

        self.applyButton.clicked.connect(self.analyzerFunc)
        
        self.show()
        

    def dialog(self,results,name,tournament_count,rating_list, result_countries):
                mtable = QTableWidget()
                mbox = QMessageBox()
                avg_opponent = sum(rating_list)/len(rating_list)
                text = ""
                tournament_count_text = "Tournaments that have been played:  {}\n".format(tournament_count)
                country_text = ""
                for i in range(len(result_countries)):
                    country_text += result_countries[i][0]+ ": "+ str(result_countries[i][1]) + "\n"
                for i  in range(len(results)):
                    text += results[i] + "\n" 
                mbox.setInformativeText("Average Opponent Rating: {:.2f}".format(avg_opponent)+"\n\n"+"MOST PLAYED OPPONENTS:\n "+text)
                mbox.setText(name.upper())
                mbox.setDetailedText(tournament_count_text + "MOST PLAYED COUNTRIES:\n"+country_text)
                mbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                mbox.exec_()

    def analyzerFunc(self):
        
        try:         
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
            url = "https://ratings.fide.com"
            driver.get(url)
            driver.delete_all_cookies()
       
            name = self.nameLineEdit.text()
            search = driver.find_element(By.ID, "dyn1")
            search.send_keys(name)
            
            driver.implicitly_wait(10)

            button = driver.find_element(By.ID, "search_form_buton")
            button.click()

            driver.implicitly_wait(10)
            
            person = driver.find_element(By.XPATH, "/html/body/section[3]/div[2]/div/div[4]/div/div[1]/div[2]/table/tbody/tr/td[1]/a")
            person_link = person.get_attribute("href") 
            driver.get(person_link)

            driver.implicitly_wait(10)
            
            ind_button = driver.find_element(By.ID, "calculations_button")
            ind_button.click()

            driver.implicitly_wait(10)

            calculations_table = driver.find_elements(By.XPATH,"//*[@id='history_div']/table/tbody/tr")
            
            links = []
            
            tournament = []
            for i in range(1,len(calculations_table)):
                calculation = driver.find_elements(By.XPATH, "//*[@id='history_div']/table/tbody/tr[{}]/td".format(i))
                if(calculation[1].text =="No Games"):
                    continue
                else:
                    calculation[1] = driver.find_element(By.XPATH, "//*[@id='history_div']/table/tbody/tr[{}]/td/a".format(i))
                    link = calculation[1].get_attribute("href")
                    links.append(link)
                    continue

            rows_text = []
            for i in range(len(links)):
                driver.get(links[i])
                driver.implicitly_wait(10)
                tournament_month = (driver.find_element(By.XPATH, '//*[@id="calc_list"]/table[2]'))
                rows = tournament_month.find_elements(By.TAG_NAME,"tr")
                for i in range (len(rows)):
                    rows_text.append(rows[i].text)
            last_index = 2
            driver.close()
            
            for i in range(2,len(rows_text)):
                if rows_text[i-1] == "Rc Ro w n chg K K*chg" or rows_text[i-1] == "Rc Ro w n chg Rp K K*chg":
                    tournament.append(rows_text[last_index:i])
                    last_index = i
            tournament.append(rows_text[last_index:])
            tournament[len(tournament)-1].append("")
            
            def find_opponents(tournament):
                opponent_list = []
                for i in range(1,len(tournament)-1):
                    for j in range(2, len(tournament[i])-2):
                        if tournament[i][j]=="Rc Ro w n chg K K*chg" or tournament[i][j]== "Rc Ro w n chg Rp K K*chg" or tournament[i][j]== "" or tournament[i][j]== ' * Rating difference of more than 400.':
                            continue
                        else:
                            opponent_list.append(tournament[i][j])
                return opponent_list
            
            opponents_list = find_opponents(tournament)
            rating_list = []
            opponent_name = []
            opponent_scores = []
            country_list = []
            for i in range(len(opponents_list)):
                
                if "0.50" in opponents_list[i]:
                    opponent_scores.append ( "0.50")
                elif "1.00" in opponents_list[i]:
                    opponent_scores.append ( "1.00")
                else:
                    opponent_scores.append ( "0.00")
                opponents_list[i] = opponents_list[i][2:len(opponents_list[i])]
                opponents_list[i] = opponents_list[i].split(" ")
                if opponents_list[i][2].isnumeric():
                    rating_list.append(int(opponents_list[i][2]))
                elif opponents_list[i][3].isnumeric():
                    rating_list.append(int(opponents_list[i][3]))
                elif opponents_list[i][4].isnumeric():
                    rating_list.append(int(opponents_list[i][4]))

                if (opponents_list[i][3].isnumeric() == False and opponents_list[i][3].isupper() and len(opponents_list[i][3])>1 ):
                    country_list.append((opponents_list[i][3]))
                elif opponents_list[i][4].isnumeric() == False and len(opponents_list[i][4])>1 and opponents_list[i][4].isupper():
                    country_list.append((opponents_list[i][4]))
                elif opponents_list[i][5].isnumeric() == False and len(opponents_list[i][5])>1 and opponents_list[i][5].isupper():
                    country_list.append((opponents_list[i][5] ))
                elif opponents_list[i][6].isnumeric() == False and opponents_list[i][6].isupper() and len(opponents_list[i][6])>1:
                    country_list.append((opponents_list[i][6]))
                elif opponents_list[i][7].isnumeric() == False and opponents_list[i][7].isupper() and len(opponents_list[i][7])>1:
                    country_list.append((opponents_list[i][7]))
                elif opponents_list[i][8].isnumeric() == False and opponents_list[i][8].isupper():
                    country_list.append((opponents_list[i][8]))
                if (opponents_list[i][1]) != ",":
                    opponent_name.append(opponents_list[i][0]+" " + opponents_list[i][1])
                else:
                    opponent_name.append(opponents_list[i][0]+" " + opponents_list[i][2])
                opponent_scores[i] = ( opponent_name[i] + " " +opponent_scores[i])
        
            counts_opponents = Counter(opponent_name)
            result_opponents = counts_opponents.most_common(20)

            set_of_opponents = set(opponent_name)
            opponents_dictionary = dict.fromkeys(set_of_opponents,0)
            for i in range(len(opponent_scores)):
                if("1.0" in opponent_scores[i]):
                    if opponent_name[i] in opponent_scores[i]:
                        opponents_dictionary[opponent_name[i]] += 1.0
            
                elif("0.5" in opponent_scores[i]):
                    if opponent_name[i] in opponent_scores[i]:
                        opponents_dictionary[opponent_name[i]] += 0.5

            results = []                    
            for i in range(len(result_opponents)):
                results.append((result_opponents[i][0] + "      Maç sayısı:  " +str(result_opponents[i][1]) +"   Skor:   " +str(opponents_dictionary[result_opponents[i][0]]) + "-" + str(result_opponents[i][1]-opponents_dictionary[result_opponents[i][0]])))    
            
            countries_count = Counter(country_list)
            result_countries = countries_count.most_common(4)

            

            
            torunament_count = len(tournament)-1
            self.dialog(results,name,torunament_count,rating_list,result_countries)
            
            



            
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText("Error!!!\nPlease check the values.")
            msg.setWindowTitle("Error")
            msg.exec_()
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MAIN = Main()
    
    
    
   

    
    
    sys.exit(app.exec_())

    