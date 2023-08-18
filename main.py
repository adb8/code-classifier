import tkinter as tk
from tkinter import filedialog
from prepare import prepare_code
import joblib
import pandas as pd
import threading
import tensorflow as tf

class Models():
    def load_models(self):
        self.vectorizer = joblib.load('models/conven/vectorizer.joblib')
        self.feature_names = joblib.load('models/conven/feature_names.joblib')
        self.knn_model = joblib.load('models/conven/knn_model.joblib')
        self.svm_model = joblib.load('models/conven/svm_model.joblib')
        self.nb_model = joblib.load('models/conven/nb_model.joblib')
        self.lr_model = joblib.load('models/conven/lr_model.joblib')
        self.nn_model = tf.keras.models.load_model('models/neural/')

class IDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python IDE - No Model Selected")
        self.geometry("800x800")
        self.iconbitmap("public/python.ico")

        self.previous_code = None
        self.current_code = None
        self.current_model = None
        self.highlighted = False
        self.secureness = "Secure"
        self.file_path = None

        self.create_widgets()
        self.bind_shortcuts()

        self.models = Models()
        self.models.load_models()
        self.check_code()

    def make_text_red(self, text_widget, start_index, end_index):
        text_widget.tag_configure("red_underline", foreground="red")
        text_widget.tag_add("red_underline", start_index, end_index)

    def make_text_normal(self, text_widget, start_index, end_index):
        text_widget.tag_remove("red_underline", start_index, end_index)

    def check_code(self):
        if self.current_model is not None and self.current_code is not None:
            if "input" not in self.current_code:
                self.secureness = "Secure"

        if self.current_model is not None and self.current_code is not None:
            if self.current_code != self.previous_code and "input" in self.current_code:

                X = self.models.vectorizer.transform([self.current_code])
                X = pd.DataFrame(X.toarray(), columns=self.models.feature_names).values
                y_pred = self.current_model.predict(X)

                if not isinstance(y_pred[0], str) and y_pred[0][0] >= 0.5:
                    self.secureness = "Secure"
                if not isinstance(y_pred[0], str) and y_pred[0][0] < 0.5:
                    self.secureness = "Insecure"
                if isinstance(y_pred[0], str) and y_pred[0] == "Secure":
                    self.secureness = "Secure"
                if isinstance(y_pred[0], str) and y_pred[0] == "Insecure":
                    self.secureness = "Insecure"
                self.previous_code = self.current_code
                print(self.secureness)

        if self.secureness == "Secure" and self.highlighted:
            self.highlighted = False
            self.make_text_normal(self.text_area, "1.0", tk.END)

        if self.secureness == "Insecure" and not self.highlighted:
            self.highlighted = True
            self.make_text_red(self.text_area, "1.0", tk.END)
        threading.Timer(1, self.check_code).start()

    def bind_shortcuts(self):
        self.bind("<Control-s>", self.save_file)
        self.text_area.bind("<KeyRelease>", self.on_keyup)

    def on_keyup(self, event=None):
        current_code = self.text_area.get("1.0", tk.END)
        self.current_code = prepare_code(current_code)

    def create_widgets(self):
        self.text_area = tk.Text(self, wrap=tk.WORD, font=("Courier", 14))
        self.text_area.pack(expand=True, fill='both')
        self.menu_bar = tk.Menu(self)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Save As...", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit_app)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.model_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.model_menu.add_command(label="K Nearest Neighbors", command=lambda: self.model_menu_callback("KNN"))
        self.model_menu.add_command(label="Support Vector Machine", command=lambda: self.model_menu_callback("SVM"))
        self.model_menu.add_command(label="Naive Bayes", command=lambda: self.model_menu_callback("NB"))
        self.model_menu.add_command(label="Logistic Regression", command=lambda: self.model_menu_callback("LR"))
        self.model_menu.add_command(label="Neural Network", command=lambda: self.model_menu_callback("NN"))
        self.menu_bar.add_cascade(label="Model", menu=self.model_menu)
        self.config(menu=self.menu_bar)

    def model_menu_callback(self, model):
        if model == "KNN":
            self.current_model = self.models.knn_model
            self.title("Python IDE - K Nearest Neighbors")

        elif model == "SVM":
            self.current_model = self.models.svm_model
            self.title("Python IDE - Support Vector Machine")

        elif model == "NB":
            self.current_model = self.models.nb_model
            self.title("Python IDE - Naive Bayes")

        elif model == "LR":
            self.current_model = self.models.lr_model
            self.title("Python IDE - Logistic Regression")
            
        elif model == "NN":
            self.current_model = self.models.nn_model
            self.title("Python IDE - Neural Network")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            self.file_path = file_path
            with open(file_path, "r") as file:
                content = file.read()
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, content)

    def save_file(self, event=None):
        if self.file_path:
            content = self.text_area.get(1.0, tk.END)
            with open(self.file_path, "w") as file:
                file.write(content)
        else:
            self.save_as_file()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            filetypes=[("Python Files", "*.py")],
            defaultextension=".py"
        )
        if file_path:
            if not file_path.endswith(".py"):
                file_path += ".py"
            self.file_path = file_path
            self.save_file()

    def quit_app(self):
        self.destroy()

if __name__ == "__main__":
    ide = IDE()
    ide.mainloop()