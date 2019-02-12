from flask import Flask,render_template,request,send_file
from geopy.geocoders import Nominatim
import  pandas
import  datetime

uygulama=Flask(__name__)

@uygulama.route("/")
def index():
    return render_template("index.html")


def uzantiKontrol(dosya):
    return '.' in dosya and dosya.rsplit('.', 1)[1].lower() in "csv"

@uygulama.route("/islem",methods=["POST"])
def islem():
    if request.method=="POST":
        if "adres" in request.form:
            if request.form["adres"]!="":
                try:
                    adres=request.form["adres"]
                    nom = Nominatim(timeout=20,scheme='http')
                    n = nom.geocode(adres,addressdetails=True)
                    if n!=None:
                        data = [[adres, n.longitude, n.latitude, n]]
                        df = pandas.DataFrame(data, columns=['Sorgulanan Adres', 'Enlem', 'Boylam', 'Tam Koordinat'])
                        pandas.set_option("display.max_colwidth", -1)
                        return render_template("index.html", koordinat=df.to_html(), durum=1)
                    else:
                        return render_template("index.html", uyari="Yazılan adresin coğrafi bilgilerine ulaşılamadı.Lütfen geçerli bir adresi düzgün bir şekilde giriniz! ", durum=1)
                except Exception as e:
                    return render_template("index.html", uyari=str(e),durum=1)
            else:
                return render_template("index.html",uyari="Lütfen bir adres giriniz!",durum=1)



@uygulama.route("/csv-sorgula",methods=["POST"])
def upload():
    if request.method == "POST":
        if 'dosya' not in request.files:
            return render_template("index.html", uyari="Lütfen cvs dosyasını seçiniz", durum=2)
        global filename
        global df
        file = request.files['dosya']
        if file.filename == '':
            return render_template("index.html", uyari="Lütfen cvs dosyasını seçiniz", durum=2)
        if file and uzantiKontrol(file.filename):
            try:
                df = pandas.read_csv(file)
                gc = Nominatim(scheme='http', timeout=30)
                df["Tam Koordinat"] = df["Adres"].apply(gc.geocode)
                df['Enlem'] = df['Tam Koordinat'].apply(lambda x: x.latitude if x != None else "None")
                df['Boylam'] = df['Tam Koordinat'].apply(lambda x: x.longitude if x != None else "None")
                df = df.drop("Tam Koordinat", 1)
                filename = datetime.datetime.now().strftime("dosyalar/%Y-%m-%d-%H-%M-%S-%f" + ".csv")
                df.to_csv(filename, index=None)
                return render_template("index.html", koordinat=df.to_html(), durum=2,indirmebaglantisi='indir.html')
            except Exception as e:
                return render_template("index.html", uyari=str(e),durum=2)
        else:
            return render_template("index.html", uyari="Lütfen sadece csv uzantılı dosyaları yükleyiniz", durum=2)


@uygulama.route("/indir")
def indir():
    return send_file(filename, attachment_filename='dosyaniz.csv', as_attachment=True)

if __name__ =="__main__":
    uygulama.run(debug=True)