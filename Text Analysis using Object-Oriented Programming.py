import tkinter as tk
from tkinter import messagebox
import requests
import json
import mysql.connector
import paralleldots

class SentimentAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sentiment Analysis App")
        self.root.geometry("400x600")
        self.root.configure(bg="lightblue")

        self.login_frame = None
        self.registration_frame = None
        self.user_name = None
        self.user_email = None

        self.__create_login_page()

        # Connect to the MySQL database
        # provide your db connection
        self.db = mysql.connector.connect(
            host="",
            user="",
            password="",
            database=""
        )
        self.cursor = self.db.cursor()
        self.cursor.execute("SHOW COLUMNS FROM users LIKE 'name'")
        if not self.cursor.fetchone():
            self.cursor.execute("ALTER TABLE users ADD name VARCHAR(255)")

    def __create_login_page(self):
        if self.registration_frame:
            self.registration_frame.destroy()
        self.login_frame = tk.Frame(self.root, width=600, height=400)
        self.login_frame.pack()

        email_label = tk.Label(self.login_frame, text="Email:")
        email_label.pack(pady=15)
        self.email_entry = tk.Entry(self.login_frame,width=40)
        self.email_entry.pack(pady=20)

        password_label = tk.Label(self.login_frame, text="Password:")
        password_label.pack(pady=15)
        self.password_entry = tk.Entry(self.login_frame, show="*",width=40)
        self.password_entry.pack(pady=20)

        login_button = tk.Button(self.login_frame, text="Login", command=self.__login)
        login_button.pack(pady=20)

        register_button = tk.Button(self.login_frame, text="Register", command=self.__create_registration_page)
        register_button.pack(pady=20)

    def __create_registration_page(self):
        if self.login_frame:
            self.login_frame.destroy()
        self.registration_frame = tk.Frame(self.root, width=600, height=400)
        self.registration_frame.pack()

        name_label = tk.Label(self.registration_frame, text="Create Name:")
        name_label.pack()
        self.name_entry = tk.Entry(self.registration_frame,width=40)
        self.name_entry.pack(pady=20)

        email_label = tk.Label(self.registration_frame, text="Create Email:")
        email_label.pack()
        self.email_entry = tk.Entry(self.registration_frame,width=40)
        self.email_entry.pack(pady=20)

        password_label = tk.Label(self.registration_frame, text="Create Password:")
        password_label.pack()
        self.password_entry = tk.Entry(self.registration_frame, show="*",width=40)
        self.password_entry.pack(pady=20)

        register_button = tk.Button(self.registration_frame, text="Register", command=self.__register)
        register_button.pack(pady=20)

        go_back_button = tk.Button(self.registration_frame, text="Go Back to Login", command=self.__create_login_page)
        go_back_button.pack(pady=20)

    def __register(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not name or not email or not password:
            messagebox.showerror("Registration Error", "Please fill in all fields.")
            return
        self.cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = self.cursor.fetchone()

        if existing_user:
            messagebox.showerror("Registration Error", "User already exists. Please log in")
        else:
            self.cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
            self.db.commit()
            self.__create_login_page()
            messagebox.showinfo("Registration Successful", "Account created successfully. You can now log in")

    def __login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Login Error", "Please fill in all fields")
            return
        
        self.cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = self.cursor.fetchone()

        if user:
            if user[3] == password:
                self.user_name = user[1]
                self.user_email = user[2]
                self.__create_sentiment_analysis_page()
                self.login_frame.destroy()
            else:
                messagebox.showerror("Login Error", "Invalid credentials. Try again")
        else:
            messagebox.showerror("Login Error", "This email is not registered")
            
    #         def __login(self):
    # email = self.email_entry.get()
    # password = self.password_entry.get()

    # if not email or not password:
    #     messagebox.showerror("Login Error", "Please fill in all fields.")
    #     return

    # self.cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    # user = self.cursor.fetchone()

    # if user:
    #     if user[3] == password:
    #         self.user_name = user[1]
    #         self.user_email = user[2]
    #         self.__create_sentiment_analysis_page()
    #         self.login_frame.destroy()
    #     else:
    #         messagebox.showerror("Login Error", "Invalid credentials. Please try again")
    # else:
    #     messagebox.showerror("Login Error", "Invalid credentials. Please try again")

    def __create_sentiment_analysis_page(self):
        if self.login_frame:
            self.login_frame.destroy()
        if self.registration_frame:
            self.registration_frame.destroy()
        
        self.sentiment_frame = tk.Frame(self.root, width=600, height=400)
        self.sentiment_frame.pack(pady=20)

        sentiment_label = tk.Label(self.sentiment_frame, text="Enter text for sentiment analysis:")
        sentiment_label.pack(pady=20)

        self.sentiment_text_entry = tk.Entry(self.sentiment_frame, width=50)
        self.sentiment_text_entry.pack()

        sentiment_button = tk.Button(self.sentiment_frame, text="Analyze Sentiment", command=self.__perform_sentiment_analysis)
        sentiment_button.pack(pady=20)
        
        ner_button = tk.Button(self.sentiment_frame, text="Named Entity Recognition", command=self.__perform_ner)
        ner_button.pack(pady=20)

        sarcasm_button = tk.Button(self.sentiment_frame, text="Detect Sarcasm", command=self.__perform_sarcasm)
        sarcasm_button.pack(pady=20)

        abuse_button = tk.Button(self.sentiment_frame, text="Detect Abuse", command=self.__perform_abuse)
        abuse_button.pack(pady=20)
        
        keywords_button = tk.Button(self.sentiment_frame, text="Get Keywords", command=self.__get_keywords)
        keywords_button.pack(pady=20)

        go_back_button = tk.Button(self.sentiment_frame, text="log out", command=self.__log_out)
        go_back_button.pack(pady=20)



    def __perform_sentiment_analysis(self):
        text = self.sentiment_text_entry.get()
        response = self.get_sentiment(text)

        if 'error' in response:
            messagebox.showerror("API Error", response['error'])
        else:
            sentiment_result = response['sentiment']
            messagebox.showinfo("Sentiment Analysis Result", f"Sentiment: {sentiment_result}")

    def get_sentiment(self, text, lang_code="en"):
        api_key = self.get_api_key()
        response = requests.post("https://apis.paralleldots.com/v4/sentiment", data={"api_key": api_key, "text": text, "lang_code": lang_code}).text
        response = json.loads(response)
        return response
    
    def __perform_ner(self):
        text = self.sentiment_text_entry.get()
        response = self.get_ner(text)
        if 'error' in response:
            messagebox.showerror("API Error", response['error'])
        else:
            messagebox.showinfo("Named Entity Recognition Result", json.dumps(response, indent=2))
    
    def get_ner(self, text, lang_code="en"):
        api_key = self.get_api_key()
        response = requests.post("https://apis.paralleldots.com/v4/ner", data={"api_key": api_key, "text": text, "lang_code": lang_code}).text
        response = json.loads(response)
        return response
     
    def __perform_sarcasm(self):
        text = self.sentiment_text_entry.get()
        response = self.get_sarcasm(text)
        if 'error' in response:
            messagebox.showerror("API Error", response['error'])
        else:
            sarcasm_score = response.get('Sarcastic', 0.0)
            non_sarcastic_score = response.get('Non-Sarcastic', 0.0)
            messagebox.showinfo("Sarcasm Detection Result", f"Sarcasm Score: {sarcasm_score:.2f}\nNon-Sarcasm Score: {non_sarcastic_score:.2f}")

    def get_sarcasm(self, text, lang_code="en"):
        api_key = self.get_api_key()
        response = requests.post("https://apis.paralleldots.com/v4/sarcasm", data={"api_key": api_key, "text": text, "lang_code": lang_code}).text
        response = json.loads(response)
        return response

    def __perform_abuse(self):
        text = self.sentiment_text_entry.get()
        response = self.get_abuse(text)
        if 'error' in response:
            messagebox.showerror("API Error", response['error'])
        else:
            abusive_score = response.get('abusive', 0.0)
            hate_speech_score = response.get('hate_speech', 0.0)
            neither_score = response.get('neither', 0.0)
            messagebox.showinfo("Abuse Detection Result", f"Abusive Score: {abusive_score:.2f}\nHate Speech Score: {hate_speech_score:.2f}\nNeither Score: {neither_score:.2f}")

    
    def get_abuse(self, text):
        api_key = self.get_api_key()
        response = requests.post("https://apis.paralleldots.com/v4/abuse", data={"api_key": api_key, "text": text}).text
        response = json.loads(response)
        return response

    def __get_keywords(self):
        text = self.sentiment_text_entry.get()
        response = self.get_keywords(text)
        if 'error' in response:
            messagebox.showerror("API Error", response['error'])
        else:
            keywords = response.get('keywords', 'Keywords not detected')
            messagebox.showinfo("Keywords Result", f"Keywords: {keywords}")
            
    def get_keywords(self,text ):
            api_key  = self.get_api_key()
            response = requests.post( "https://apis.paralleldots.com/v4/keywords", data= { "api_key": api_key, "text": text } ).text
            response = json.loads( response )
            return response


    def get_api_key(self):
        return ""

    def __log_out(self):
        self.sentiment_frame.pack_forget()
        self.__create_login_page()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = SentimentAnalysisApp(root)
    app.run()
