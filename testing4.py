import csv
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, filedialog
import pyodbc

server_name = 'DESKTOP-FC3VM4U\SQLEXPRESS'
database_name = 'FILES'

#verbindungs string mit windows authentif.
conn_str ='Driver={SQL Server};Server=' + server_name + ';Database=' + database_name + ';Trusted_Connection=yes;'

#sql server verbinden
conn=pyodbc.connect(conn_str)

#cursor objekt erzeugen
cursor = conn.cursor()

filenames=[]

#csv importieren
def import_csv():
    #datei auswaehlen fenster
    global filenames
    global table_name_filemanager


    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

    #falls keine datei ausgewählt dann nichts
    if not file_path:
        return

    #ordner auf pc
    filename = os.path.basename(file_path)
    filenames.append(filename)
    messagebox.showinfo("Sie waren erfolgreich")

    # tabellen namen erstellen
    table_name_filemanager = f'files{value_acc[0]}'

    # check ob tabelle in db schon existiert
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name_filemanager}'")
    table_exists = cursor.fetchone()[0] > 0

    if not table_exists:
        # befehl um neue tabelle in db zu erstellen
        create_table_sql = f"CREATE TABLE {table_name_filemanager} (filename VARCHAR(50) PRIMARY KEY);"
        try:
            # befehl ausführen um neue tabelle in db zu erstellen
            cursor.execute(create_table_sql)
        except Exception as e:
            # fehlermeldung
            print(f"Fehler bei Erstellung: {e}")
        else:
            print("Tabelle erstellt!")

    # sql befehl um datei in die db tabelle hinzuzüfügen
    insert_statement_sql = f"INSERT INTO {table_name_filemanager} (filename) VALUES (?);"
    cursor = conn.cursor()
    # befehl ausführen um datei in die db tabelle
    try:
        cursor.execute(insert_statement_sql, (filename))
        cursor.commit()
    except Exception as e:
        # fehlermeldung
        print(f"Fehler beim Einfügen: {e}")

    #datei in die DB importieren
    #csv datei öffnen
    with open(file_path, 'r') as f:
        # erster zeile der csv datein lesen um die anzahl der spalten zu bestimmen
        reader = csv.reader(f, delimiter = ',')
        #spaltenanzahl ausgeben
        num_cols = len(next(reader))

        row_values_all = []
        first_row = next(reader)
        row_values_all.append(first_row)

        for row in reader:
            row_values = []
            for value in row:
                row_values.append(value)

            row_values_all.append(row_values)

        global table_name
        #eindeutigen tabellennamen erstellen abhängig von datum und zeit
        table_name = datetime.now().strftime("importeddata_%Y%m%d_%H%M%S")

        #tabelle in sql erzeugen
        create_table_sql = f"CREATE TABLE {table_name} (id INT IDENTITY(1,1) PRIMARY KEY,"
        for i in range(num_cols):
            column_data_type = "NVARCHAR(MAX)"  # annahme dass alle spalten nvarchar
            create_table_sql += f"col{i} {column_data_type},"
        create_table_sql = create_table_sql[:-1] + ")"  #abschließendes komma entfernen und klammern schließen

        #ausführem d. tabelle erstellen sql befehls
        cursor = conn.cursor()
        cursor.execute(create_table_sql)

        #iterieren durch jede zeile des csv und diese in sql server einfügen
        num_of_columns = num_cols
        placeholders = ",".join("?" * num_of_columns)
        insert_statement = f"INSERT INTO {table_name} VALUES ({placeholders})"

        for row in row_values_all:
            row_values = row
            cursor = conn.cursor()
            cursor.execute(insert_statement, *row_values)
            cursor.commit()


#funktion um alle importierten dateien anzuzeigen
def File_Manager():
    #datei manager fenster
    root2 = tk.Tk()
    root2.geometry("300x300")
    root2.title("Datei Manager")
    root2.config(bg="#34495E")


    #label um importierte csv anzuzeigen
    Label_of_filemanager = tk.Label(root2, text="Liste aller  CSV's", font=("Calibri", 16, "bold"),
                                    bg="#34495E", fg="white")
    Label_of_filemanager.pack(padx=20, pady=15)

    try:
        query = f"SELECT * FROM files{value_acc[0]};"
        cursor.execute(query)
        # Fetch all rows from the result set
        rows = cursor.fetchall()
        values = [row[0] for row in rows]
        print(values)
        # ueber alle csv iterieren
        for i in range(len(values)):
            # create a label to display each CSV file name
            label = tk.Label(root2, text=f'{i + 1})  {values[i]}', font=("Arial", 12), bg="#34495E", fg="white")
            # add padding to the label
            label.pack(padx=20, pady=10)
    except Exception as e:
        label = tk.Label(root2, text="Keine CSV's importiert", font=("Arial", 12), bg="#34495E", fg="white")
        # add padding to the label
        label.pack(padx=20, pady=10)
        print(e)


    root2.mainloop()

#funktion fuer suchleiste
def search_csv():
    #ergebnis der suche mit get
    searched_value = search_bar.get()


    #leere liste initialisieren um dateien hinzuzufügen
    matching_files = []

    #check ob gesuchter wert nicht leer
    if searched_value != "":
        #neues fenster fuer suchergebnisse
        root3 = tk.Tk()
        root3.geometry("300x300")
        root3.title("Suchergebnisse")
        root3.config(bg="#34495E")

        query = f"SELECT * FROM files{value_acc[0]};"
        cursor.execute(query)
        # Fetch all rows from the result set
        rows = cursor.fetchall()
        values = [row[0] for row in rows]
        for i in values:
            filenames.append(i)

        #ueber alle csv dateien iterieren
        for results in filenames:
            result=results.upper()
            value_searched_upper=searched_value.upper()
            #check ob gesuchter wert in csv datei namen enthalten
            if value_searched_upper in result:
                #csv file zu liste hinzufügen
                matching_files.append(results)

        #check ob übereinstimmende dateien
        if matching_files != []:
            #label um suchergebnisse anzuzeigen
            search_label = tk.Label(root3, text="Suchergebnisse", font=("Helvetica", 12, "bold"),bg="#34495E", fg="white")
            search_label.pack(padx=20, pady=15)

            #durch alle übereinstimmende dateien iterieren
            for i in range(len(matching_files)):
                #label um jede uebereinstimmende datei anzuzeigen
                label1 = tk.Label(root3, text=matching_files[i], font=("Arial", 12), bg="#34495E", fg="white")
                label1.pack(padx=20, pady=10)

            root3.mainloop()

        else:
            # label um zu zeigen dass suchergebnisse angezeigt werden
            search_label = tk.Label(root3, text="Suchergebnisse ", font=("Arial", 12, "bold"), bg="#34495E", fg="white")
            search_label.pack(padx=20, pady=15)

            # labem um zu zeigen dass keine übereinstimmende files
            search_label_1 = tk.Label(root3, text="Keine solche Datei", font=("Arial", 12), bg="#34495E", fg="white")
            search_label_1.pack(padx=20, pady=15)

    else:
        messagebox.showerror("Fehler!" , "Bitte Datei eingeben")

#funktion um neuen acc in db tabelle
def account_creation():
    #gettern mail und passwort eingabe
    email_signup = email_value_signup.get()
    password_signup = password_value_signup.get()

    #check ob mail und pw nicht ausgefüllt
    if email_signup == "" or password_signup == "":
        messagebox.showerror("Fehler!", "Bitte ausfüllen")

    else:
        #tabellen namen erstellen
        table_name_signup = "Accountsdata"

        #check ob tabelle in db schon existiert
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name_signup}'")
        table_exists = cursor.fetchone()[0] > 0

        if not table_exists:
            #befehl um neue tabelle in db zu erstellen
            create_table_sql = f"CREATE TABLE {table_name_signup} (email VARCHAR(50) PRIMARY KEY,password VARCHAR(50));"
            try:
                #befehl ausführen um neue tabelle in db zu erstellen
                cursor.execute(create_table_sql)
            except Exception as e:
                #fehlermeldung
                print(f"Fehler bei Erstellung: {e}")
            else:
                print("Tabelle erstellt!")


        #sql befehl um datei in die db tabelle hinzuzüfügen
        insert_statement_sql = f"INSERT INTO {table_name_signup} (email, password) VALUES (?, ?);"
        cursor = conn.cursor()
        #befehl ausführen um datei in die db tabelle
        cursor.execute(insert_statement_sql, (email_signup , password_signup))
        cursor.commit()
        #meldung erfolgreich
        messagebox.showinfo("Erfolgreich", "Benutzer erstellt")
        root4.destroy()

#GUI neuer benutzer
def sign_up_screen():
    global root4
    root4 = tk.Tk()
    root4.geometry("400x250")
    root4.title("Registrieren")
    root4.config(bg="#34495E")

    #zugang zu global var
    global email_value_signup
    global password_value_signup

    #label für registrieren
    Label_header = tk.Label(root4, text="Registrieren", font=("Arial", 20, "bold"), bg="#34495E", fg="white")
    Label_header.place(x=100, y=10)

    #label und feld für email
    email_signup = tk.Label(root4, text="Email", font=("Arial", 12), bg="#34495E", fg="white")
    email_signup.place(x=30, y=80)

    email_value_signup = tk.Entry(root4, width=28, font=("Arial", 12))
    email_value_signup.place(x=130, y=80)

    #label und feld fuer pw
    password_signup = tk.Label(root4, text="Passwort", font=("Arial", 12), bg="#34495E", fg="white")
    password_signup.place(x=30, y=130)

    password_value_signup = tk.Entry(root4, width=28, font=("Arial", 12), show="*")
    password_value_signup.place(x=130, y=130)

    #button fuer registrierung und neuer benutzer erstellen ausfuehren
    sign_button = tk.Button(root4, text="Benutzer erstellen", command=account_creation, font=("Arial", 12), bg="#5D6D7E", fg="white", padx=10, pady=5, bd=1, width=15)
    sign_button.place(x=120, y=190)

    root4.mainloop()

#dashboard
def toggle_dashboard():
    global search_bar #zugang erlauben
    global email

    global value_acc


    #get email und pw von eingangs widget
    email = email_value.get()
    value_acc = email.split(sep="@")
    password = password_value.get()

    table_name_signup = "Accountsdata"

    #sql query ob mail und pw stimmen
    select_sql = f"SELECT email FROM {table_name_signup} WHERE email = ? AND password = ?"

    #ausführen query und ergebnisse aufrufen
    cursor = conn.cursor()
    cursor.execute(select_sql, (email, password))
    result = cursor.fetchone()

    # check ob zeile zurückgegeben
    if result:
        # falls zeile zurückgegeben dann email und pw passen zusamen
        messagebox.showinfo("Willkommen ", "Anmeldung erfolgreich")
        # close the main window
        root.destroy()
        # neues fenster fuer dashboard
        root1 = tk.Tk()
        root1.geometry("330x300")
        root1.title("CSV Importer")
        root1.config(bg="#34495E")

        # datei manager button
        file_manager_button = tk.Button(root1, text="Datei Manager", command=File_Manager, font=("Arial", 12),bg="#5D6D7E", fg="white", padx=10, pady=5, bd=1, width=10)
        file_manager_button.pack(padx=20, pady=20)

        # importieren button
        import_button = tk.Button(root1, text="Importieren", command=import_csv, font=("Arial", 12), bg="#5D6D7E", fg="white", padx=10, pady=5, bd=1, width=10)
        import_button.pack(padx=20, pady=20)

        # log out button
        logout_button = tk.Button(root1, text="Log out", command=root1.destroy, font=("Arial", 12), bg="#5D6D7E", fg="white", padx=10, pady=5, bd=1, width=10)
        logout_button.pack(padx=20, pady=20)

        # suchleiste und button
        search_var = tk.StringVar()
        search_bar = tk.Entry(root1, textvariable=search_var, font=("Arial", 12))
        search_bar.pack(side=tk.LEFT, padx=20, pady=20)
        search_button = tk.Button(root1, text="Suchen", command=search_csv, font=("Arial", 12), bg="#5D6D7E",  fg="white", padx=10, pady=5, bd=1, width=7)
        search_button.pack(side=tk.LEFT, padx=10, pady=20)

        root1.mainloop()
    else:
        # falls keine zeile zurückgegeben dann email und pw falsch
        messagebox.showerror("FEHLER!!!", "Korrekte Email und Passwort eingeben")


# Hauptfenster
root = tk.Tk()
root.geometry("400x250")
root.title("CSV Importer")
root.config(bg="#34495E")

# email und passwort widgets
email = tk.Label(root, text="Email", font=("Arial", 12), bg="#34495E", fg="white")
email.place(x=30, y=30)

email_value = tk.Entry(root, width=28, font=("Arial", 12))
email_value.place(x=130, y=30)

password = tk.Label(root, text="Passwort", font=("Arial", 12), bg="#34495E", fg="white")
password.place(x=30, y=90)

password_value = tk.Entry(root, width=28, show="*", font=("Arial", 12))
password_value.place(x=130, y=90)

# login button
login_button = tk.Button(root, text="Login", command=toggle_dashboard, font=("Arial", 12), bg="#5D6D7E", fg="white", padx=10, pady=5, bd=1, width=7)
login_button.place(x=150, y=150)

# reg button
signup_button = tk.Button(root, text="Registrieren", command=sign_up_screen, font=("Arial", 12), bg="#5D6D7E", fg="white", padx=10, pady=5, bd=1, width=7)
signup_button.place(x=150, y=200)

root.mainloop()






