from django.shortcuts import render, redirect,reverse
from .models import Personal_information, Appointment
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .forms import Createform, Create_appoint_form
from datetime import datetime, timedelta
from django.core.paginator import Paginator
import matplotlib
import matplotlib.pyplot as plt
import io
from io import BytesIO
import urllib,base64
import pandas as pd
import statistics
import numpy as np
import joypy
import seaborn as sns
import csv
from my_app.pdfs import NextDayPrint, PrevYearPrint
matplotlib.use('Agg')


def home(request):
   date1, a = check_availability()
   if date1 is None:
       date_value = "No availability"
   else:
       date_value = date1
   dose_l=[]
   if datetime.now().weekday() == 4:
       date2=datetime.now().date() + timedelta(days=3)
   elif datetime.now().weekday() == 5:
       date2 = datetime.now().date() + timedelta(days=2)
   else:
       date2 = datetime.now().date() + timedelta(days=1)
   obj = Appointment.objects.filter(date_time__contains=date2)
   for i in obj:
       dose_l.append(i.dose)
   dose = sum(dose_l)
   bmi = []
   date3 = datetime.now().year
   obj1 = Appointment.objects.filter(date_time__contains=date3)
   for i in obj1:
       bmi.append(i.bmi)
   avg_bmi = np.mean(bmi)

   prev_year1 = datetime.now() - timedelta(days=365)
   prev_year = prev_year1.year
   print(prev_year)



   return render(request, 'base.html', {"date": date_value, "dose":dose,"avg_bmi":avg_bmi, "clock":datetime.now(), "prev_year":prev_year})


def view_all(request):
   personal_info_list = Personal_information.objects.all()
   count = len(personal_info_list)
   paginator = Paginator(personal_info_list, 25)  # Show 25 contacts per page.

   page_number = request.GET.get('page')
   personal_info = paginator.get_page(page_number)
   return render(request, 'my_app/index.html', {"personal_info": personal_info, "count":count, "clock":datetime.now()})


@csrf_exempt
def delete(request, p_id):
   try:
       Personal_information.objects.get(id=p_id).delete()
       messages.success(request, f'Patient {p_id} deleted successfully')
       if "DelUpd" in request.POST:
           return redirect("home")
       else:
           return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
   except:
       messages.error(request, f"Please, first delete all appointments of patient {p_id}")
       return redirect("/update/" + f"{p_id}" + "#history")


def add_patient(request):

   form = Createform(request.POST or None) #, initial={'id': 123}
   if request.method == "POST":
       pat_id = request.POST.get("id")
       if form.is_valid():
           if 'Sub1' in request.POST:
               form.save()
               messages.success(request, f'Patient {pat_id} registered successfully')
               return redirect("home")
               # return render(request,"my_app/add_new.html", {})
           elif 'App1' in request.POST:
               date1, a = check_availability()
               if date1 is None:
                   messages.error(request, f"No more available bookings..Latest booking scheduled on {a}")
                   return redirect("home")
               else:
                   form.save()
                   messages.success(request, f'Patient {pat_id} registered successfully')
                   return redirect("/createappoint/" + f"{pat_id}" + "#book")

       else:
           # pat_id = request.POST.get("id")
           messages.error(request, f'Patient {pat_id} already exists')
           return redirect("/update/" + f"{pat_id}" + "#pat_info")
   return render(request, "my_app/add_new.html", {"form": form, "clock":datetime.now()})


def get_id(request):
   t_id = request.POST.get('checkbox')
   try:
       if t_id == None:
           return redirect("home")
       Personal_information.objects.get(id=t_id)
       # print(t_id)
       return redirect("/update/" + f"{t_id}" + "#pat_info")
       # return redirect("update", p_id=t_id)
   except:
       messages.error(request, f"Patient {t_id} not found")

       return render(request, "my_app/add_new.html/", {"id":t_id})
       # return redirect("add")
   # context={}

def update_patient(request, p_id):
   appoint_info = Appointment.objects.filter(amka_id=p_id).order_by("-date_time")
   patient = Personal_information.objects.get(id=p_id)
   form = Createform(request.POST or None, instance=patient)

   # print(form)
   if request.method == "POST":
       if form.is_valid():
           form.save()
           if 'Sub' in request.POST:
               messages.success(request, f'Patient {p_id} updated successfully')
               return redirect("/update/" + f"{p_id}" + "#pat_info")
               # return redirect("update", p_id=p_id)

           elif 'App' in request.POST:
               if form.has_changed():
                   # print("yoooo",form.changed_data)
                   messages.success(request, f'Patient {p_id} updated successfully')
               return redirect("/createappoint/" + f"{p_id}" + "#book")

               # return redirect("create_appointment", p_id=p_id)

       else:
           messages.error(request, "Please check fields again...")
           return redirect("/update/" + f"{p_id}" + "#pat_info")
           # return redirect("update", p_id=p_id)
   return render(request, "my_app/update.html",
                 {"form": form, 'patient': patient, "p_id": p_id, "appoint_info": appoint_info, "clock":datetime.now()})


def view_all_appoints(request):
   appoint_info_list = Appointment.objects.all().order_by("-date_time")
   paginator = Paginator(appoint_info_list, 25)  # Show 25 contacts per page.

   page_number = request.GET.get('page')
   appoint_info= paginator.get_page(page_number)
   return render(request, 'my_app/index_appoints.html', {"appoint_info": appoint_info, "clock":datetime.now()})


def create_appoint(request, p_id):  # ,appoint_date
   patient = Personal_information.objects.get(id=p_id)
   form = Createform(request.POST or None, instance=patient)
   appoint_form = Create_appoint_form (request.POST or None)
   date1, a = check_availability() # Unpacking return values from method checkavilability which are 2,date1= date and  a=latest_dt
   # print(type(date1))
   # print(date1.year)
   if date1 is None:
       messages.error(request, f"No more available bookings..Latest booking scheduled on {a}")
       return redirect("/update/" + f"{p_id}" + "#history")
   else:
       date = date1.strftime('%Y-%m-%d %H:%M:%S')
       context = {"form": form, "appoint_date": date,"p_id":p_id, "clock":datetime.now()}
       if request.method == "POST":
           if appoint_form.is_valid():

               appoint_form.save()
               messages.success(request, f'Appointment for patient {p_id} booked for {date}!')
               return redirect("/update/" + f"{p_id}" + "#history")
           else:
               print(appoint_form.errors)
               messages.error(request, "Errors in fields")
               return redirect("/createappoint/" + f"{p_id}" + "#book")
               # return redirect("create_appointment", p_id=p_id)
       return render(request, "my_app/create_appointment.html", context)


def check_availability():
   # start checking date availability #

   b = Appointment.objects.latest("date_time")
   a = b.date_time.strftime('%Y-%m-%d %H:%M:%S')  # get latest date time correctly by converting it to this string format
   latest_dt = datetime.strptime(a, '%Y-%m-%d %H:%M:%S')  # convert string format to date-time again
   date_time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # string
   dt_now = datetime.strptime(date_time_now,'%Y-%m-%d %H:%M:%S') # + timedelta(days=3) # convert string to date time for difference calculation
   # diff = abs(latest_dt - dt_now)
   # remaining_time_to_hours = diff.seconds / 3600  # unfortunately time.delta has no hour attribute but has seconds,therefore we need to convert seconds to hours
   # print(diff.days)
   # print(type(diff.days))

   dt_now_1 = dt_now.replace(hour=16, minute=0, second=0)
   dt_avail = dt_now + timedelta(days=14)
   dt_avail_1 = dt_avail.replace(hour=16, minute=0, second=0)
   if dt_avail_1 < latest_dt:
       print("shit")
       # messages.error(request, "Error there")
       return None,latest_dt
   elif dt_avail_1 > latest_dt > dt_now_1 : #and latest_dt.year >= dt_now.year and latest_dt.month >= dt_now.month and latest_dt.day > dt_now.day
       if latest_dt.hour < 16:
           # form.save()
           book_appoint_next_hour_same_day = latest_dt + timedelta(hours=1)
           date = book_appoint_next_hour_same_day
           return date,latest_dt
       elif latest_dt.hour == 16:
           if latest_dt.weekday() == 4 : #and (latest_dt.day + 3) <= dt_avail.day
               # form.save()
               book_appoint_after_weekend = latest_dt + timedelta(days=2, hours=17)
               date = book_appoint_after_weekend
               return date,latest_dt
           elif latest_dt.weekday() < 4:
               # form.save()
               book_appoint_next_day_of_latest = latest_dt + timedelta(hours=17)
               date = book_appoint_next_day_of_latest
               return date,latest_dt
           else:
               # messages.error(request, "Error here")
               return None, latest_dt

   elif dt_avail_1 == latest_dt:
       # messages.error(request, "No more available bookings")
       return None, latest_dt
   else:

       if dt_now.weekday() == 4:
           book_on_monday = dt_now + timedelta(days=3)
           book_appoint_on_monday = book_on_monday.replace(hour=9, minute=0, second=0)
           date = book_appoint_on_monday
           return date,latest_dt
           #else
       book_tomorrow = dt_now + timedelta(days=1)
       book_appoint_tomorrow = book_tomorrow.replace(hour=9, minute=0, second=0)
       date = book_appoint_tomorrow
       return date,latest_dt


       # end checking date availability#

@csrf_exempt
def delete_appoint(request, appoint_id):
   obj = Appointment.objects.get(id=appoint_id)
   amka = obj.amka_id  # get id for redirection
   obj.delete()  # delete appointment
   # or Appointment.objects.get(id=appoint_id).delete()
   messages.success(request, f'Appointment {appoint_id} deleted successfully')
   if 'Del' in request.POST:
       return redirect("/viewappoints/" + "#view_appoints_top")
   else:
       return redirect("/update/" + f"{amka}" + "#history")
       # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
       # return redirect("home")


def plots(request):
   age_10_20 = Personal_information.objects.filter(age__gte=10, age__lte=20).count()
   age_20_30 = Personal_information.objects.filter(age__gt=20, age__lte=30).count()
   age_30_40 = Personal_information.objects.filter(age__gt=30, age__lte=40).count()
   age_40_50 = Personal_information.objects.filter(age__gt=40, age__lte=50).count()
   age_50_60 = Personal_information.objects.filter(age__gt=50, age__lte=60).count()
   age_60 = Personal_information.objects.filter(age__gt=60).count()

   all_patients = Personal_information.objects.all().count()

   x = ((age_10_20 / all_patients) * 100, (age_20_30 / all_patients) * 100, (age_30_40 / all_patients) * 100,
        (age_40_50 / all_patients) * 100, (age_50_60 / all_patients) * 100, (age_60 / all_patients) * 100)
   labels = ['10 - 20', ' 20 - 30', ' 30 - 40', ' 40 - 50', ' 50 - 60', ' > 60']

   plt.pie(x, labels=labels, colors=["lightgreen", "deepskyblue", "tomato", "plum", "lightcoral", "khaki"],
           shadow=True, explode=(0, 0.15, 0, 0.1, 0, 0.15), startangle=80, autopct='%1.1f%%', radius=1)
   # , counterclock = False
   ttl= plt.title("Patient Ages")
   ttl.set_position([.5, 1.05])

   fig = plt.gcf()
   fig.set_size_inches(8.5, 5.5)
   buf = io.BytesIO()
   fig.savefig(buf, format='png')
   buf.seek(0)
   string = base64.b64encode(buf.read())
   uris = urllib.parse.quote(string)
   plt.close()
   data1 = plot_total_dose_per_year()
   data2 = plot_dose_per_day()
   data3 = plot_2week_dose()
   data4 = plot_age_bmi_density()
   data5 = plot_age_bmi_violin()
   data6 = plot_3d()
   data7 = plot_year_bmi_destr()

   return render(request,"my_app/plots.html", {"data":uris, "data1":data1, "data2":data2, "data3":data3,"data4":data4,"data5":data5,"data6":data6,"data7":data7, "clock":datetime.now()})

def plot_total_dose_per_year():
   dpp_curr_year=[]
   dpp_prev_year=[]
   prev_year_date = datetime.now().date() - timedelta(days=365)
   prev_year = str(prev_year_date.year)
   current_year = str(datetime.now().year)
   obj=Appointment.objects.filter(date_time__contains=prev_year)
   obj1=Appointment.objects.filter(date_time__contains=current_year)

   for i in obj1:
       dpp_curr_year.append(i.dose)

   for i in obj:
       dpp_prev_year.append(i.dose)
   total_dose_prev_year = sum(dpp_prev_year)
   total_dose_2018 = 2400 * 240
   total_dose_curr_year = sum(dpp_curr_year)
   dose = (total_dose_2018, total_dose_prev_year, total_dose_curr_year)
   years = ("2018", prev_year, current_year)
   width = [0.3, 0.7]
   y_pos=np.arange(len(years))
   fig,ax = plt.subplots()
   # fig = matplotlib.pyplot.gcf()
   ax.barh(y_pos, dose, align='center', height= 0.6)
   ax.set_xlim(0,700000)
   ax.set_yticks(y_pos)
   ax.set_yticklabels(years)
   ax.invert_yaxis()  # labels read top-to-bottom
   ax.set_xlabel('Dose (MBq)', fontsize=15)
   ax.set_ylabel('Year', fontsize=15)
   ax.set_title('Summary of total dose per year', fontsize=18)

   diff= (total_dose_prev_year * 100) / total_dose_2018 # calculate the percentage diff between previoys year and  year 2018
   f_perc = diff - 100
   f_perc = round(f_perc,2)

   for i, v in enumerate(dose):
       if v==total_dose_prev_year:
           v = round(v, 3)
           ax.text(v + 3, i, " " + str(v), color='#096daa', fontweight='bold')
           ax.text( v,i, "                   * Diff from year 2018:  "+ str(f_perc) + "%", color='#e57373', fontweight='bold', fontsize='x-large')

       else:
           v=round(v,3)
           ax.text(v + 3, i, " " + str(v), color='#096daa', fontweight='bold')
   fig.set_size_inches(18.5, 6.5)
   buf = io.BytesIO()
   fig.savefig(buf, format='png')
   buf.seek(0)
   string = base64.b64encode(buf.read())
   uris = urllib.parse.quote(string)
   plt.close()
   return uris
   # return render(request, "my_app/plots.html", {"data1": uris})
   # dose2019= statistics.mean(bmisl)

   # print(dose2019)
   # print(total_dose2019)
   # for i in bmis:
   #     bmisl.append(i)
   # print(bmisl)


def plot_dose_per_day():
   count = 0
   count1 = 0
   daily_total_dose_curr_year = []
   dose_per_pat_curr_year = []
   daily_total_dose_prev_year = []
   dose_per_pat_prev_year = []
   prev_year_date = datetime.now().date() - timedelta(days=365)
   prev_year = str(prev_year_date.year)
   current_year = str(datetime.now().year)
   obj = Appointment.objects.filter(date_time__contains=prev_year)
   obj1 = Appointment.objects.filter(date_time__contains=current_year)


# convert list to list of list of 8 indexes each //8 patients per day
   for i in obj:
       dose_per_pat_prev_year.append(i.dose)
       count += 1
       if count == 8:
           daily_total_dose_prev_year.append(sum(dose_per_pat_prev_year))
           dose_per_pat_prev_year = []
           count = 0
   print(daily_total_dose_prev_year)

   for i in obj1:
       dose_per_pat_curr_year.append(i.dose)
       count1 += 1
       if count1 == 8:
           daily_total_dose_curr_year.append(sum(dose_per_pat_curr_year))
           dose_per_pat_curr_year = []
           count1 = 0
   print(daily_total_dose_curr_year)

   x1 = [x for x in range(1, len(daily_total_dose_prev_year)+1)]
   x2 = [x for x in range(1, len(daily_total_dose_curr_year)+1)]
   # for i in x1[0::10]:


   y1 = daily_total_dose_prev_year
   y2 = daily_total_dose_curr_year
   plt.subplot(2, 1, 1)
   plt.plot(x1,y1, '.-', label=f"Year {prev_year}")
   plt.title(f'Summary of dose per day for years {prev_year} and {current_year}', fontsize=18)
   plt.ylabel('Dose (MBq)', fontsize=14)
   plt.legend(loc="upper right")
   plt.xlim(0, len(daily_total_dose_prev_year)+12)

   # plt.xticks([x1[0],x1[-1]], visible=True)

   plt.subplot(2, 1, 2)
   plt.plot(x2, y2, '.-', label=f"Year {current_year}", color='#78bf99')
   plt.xlabel('Day', fontsize=14)
   plt.ylabel('Dose (MBq)', fontsize=14)
   plt.xlim(0,len(daily_total_dose_curr_year)+10)
   plt.legend(loc="upper right")
   fig=plt.gcf()
   # from pylab import rcParams
   # rcParams['figure.figsize'] = 20, 10
   fig.set_size_inches(18.5, 6.5)
   buf = io.BytesIO()
   fig.savefig(buf, format='png')
   buf.seek(0)
   string = base64.b64encode(buf.read())
   uris = urllib.parse.quote(string)
   plt.close()
   return uris

def plot_2week_dose():
   count = 0
   count1 = 0
   two_week_total_dose_curr_year = []
   dose_per_pat_curr_year = []
   two_week_total_dose_prev_year = []
   dose_per_pat_prev_year = []
   prev_year_date = datetime.now().date() - timedelta(days=365)
   prev_year = str(prev_year_date.year)
   current_year = str(datetime.now().year)
   obj = Appointment.objects.filter(date_time__contains=prev_year)
   obj1 = Appointment.objects.filter(date_time__contains=current_year)

   for i in obj:
       dose_per_pat_prev_year.append(i.dose)
       count += 1
       if count == 80:
           two_week_total_dose_prev_year.append(sum(dose_per_pat_prev_year))
           dose_per_pat_prev_year = []
           count = 0
   print(two_week_total_dose_prev_year)

   for i in obj1:
       dose_per_pat_curr_year.append(i.dose)
       count1 += 1
       if count1 == 80:
           two_week_total_dose_curr_year.append(sum(dose_per_pat_curr_year))
           dose_per_pat_curr_year = []
           count1 = 0
   print(two_week_total_dose_curr_year)

   X = np.arange(start=1,stop=len(two_week_total_dose_prev_year)+1)
   fig, ax = plt.subplots()
   ax.bar(X -0.15, two_week_total_dose_prev_year, color='#096daa', width=0.35, label=f"Year {prev_year}")
   X1 = np.arange(start=1, stop=len(two_week_total_dose_curr_year)+1)
   ax.bar(X1+0.18, two_week_total_dose_curr_year, color='#78bf99', width=0.35, label=f"Year {current_year}")
   ax.set_ylim(17500,20500)
   ax.legend(loc="upper right")
   ax.set_ylabel('Dose (MBq)', fontsize=15)
   ax.set_xlabel('Two-week', fontsize=14)
   ax.set_title('Summary of total dose every 2 Weeks',fontsize=18)

   list1 = [x for x in range(1,25)]
   print(list1)
   print(type(list1))
   # for i in range(1,25):
   #     list1.append(i)
   ax.set_xticks(list1)
   plt.xticks(rotation=45)
   # ax.xaxis.set_ticks_position("middle")
   fig.set_size_inches(18.5, 6.5)
   buf = io.BytesIO()
   fig.savefig(buf, format='png')
   buf.seek(0)
   string = base64.b64encode(buf.read())
   uris = urllib.parse.quote(string)
   plt.close()
   return uris




def plot_age_bmi_density():
   list1=[]
   ages_10_20 = Personal_information.objects.filter(age__gte=10, age__lte=20)
   ages_20_30 = Personal_information.objects.filter(age__gt=20, age__lte=30)
   ages_30_40 = Personal_information.objects.filter(age__gt=30, age__lte=40)
   ages_40_50 = Personal_information.objects.filter(age__gt=40, age__lte=50)
   ages_50_60 = Personal_information.objects.filter(age__gt=50, age__lte=60)
   ages_60 = Personal_information.objects.filter(age__gt=60)
   print(ages_10_20)
   list3=[]
   for i in ages_10_20:
       list1.append(i.bmi)
       list1.append("age_10_20")
       list1.append(i.sex)
       list3.append(list1)
       list1=[]

   for i in ages_20_30:
       list1.append(i.bmi)
       list1.append("age_20_30")
       list1.append(i.sex)
       list3.append(list1)
       list1=[]

   for i in ages_30_40:
       list1.append(i.bmi)
       list1.append("age_30_40")
       list1.append(i.sex)
       list3.append(list1)
       list1=[]

   for i in ages_40_50:
       list1.append(i.bmi)
       list1.append("age_40_50")
       list1.append(i.sex)
       list3.append(list1)
       list1=[]

   for i in ages_50_60:
       list1.append(i.bmi)
       list1.append("age_50_60")
       list1.append(i.sex)
       list3.append(list1)
       list1=[]

   for i in ages_60:
       list1.append(i.bmi)
       list1.append("age_60")
       list1.append(i.sex)
       list3.append(list1)
       list1=[]
   df = pd.DataFrame(list3, columns=["Bmi","Age","Sex"])
   print(df)


   # plt.figure(figsize=(16, 10), dpi=80)
   fig, axes = joypy.joyplot(df, column=['Bmi','Age'], by="Age", ylim='own', figsize=(12, 3), linecolor="black",color="#e8ac54")# #e8ac54 #a36e43
   fig.set_size_inches(18.5, 6.5)
   plt.title('Density Plot of Bmi with Multiple Age Categories',fontsize=18)
   plt.xlabel('Bmi', fontsize=15)
   plt.ylabel('Density', fontsize=15)
   buf = io.BytesIO()
   fig.savefig(buf, format='png')
   buf.seek(0)
   string = base64.b64encode(buf.read())
   uris = urllib.parse.quote(string)
   plt.close()
   return uris



def plot_year_bmi_destr():
   bmis_current_year= []
   bmis_prev_year = []
   prev_year_date = datetime.now().date() - timedelta(days=365)
   prev_year = str(prev_year_date.year)
   current_year = str(datetime.now().year)
   obj = Appointment.objects.filter(date_time__contains=prev_year)
   obj1 = Appointment.objects.filter(date_time__contains=current_year)
   bmis = []
   for i in obj:
       bmis_prev_year.append(i.bmi)
       bmis_prev_year.append(prev_year)
       bmis.append(bmis_prev_year)
       bmis_prev_year=[]
   for i in obj1:
       bmis_current_year.append(i.bmi)
       bmis_current_year.append(current_year)
       bmis.append(bmis_current_year)
       bmis_current_year =[]
   df = pd.DataFrame(bmis, columns=["Bmis", "Year"])
   years=[prev_year,current_year]
   for year in years:
       subset = df[df['Year'] == year]
       sns.distplot(subset['Bmis'], hist=False, kde=True,
                    kde_kws={'shade':True,'linewidth': 2},
                    label=year)

   plt.legend(title='Year') #prop={'size': 9},
   plt.title('Bmi Yearly Distribution',fontsize=18)
   plt.xlabel('Bmi', fontsize=15)
   plt.ylabel('Density', fontsize=15)
   fig = plt.gcf()
   fig.set_size_inches(18.5, 6.5)
   buf = io.BytesIO()
   fig.savefig(buf, format='png')
   buf.seek(0)
   string = base64.b64encode(buf.read())
   uris = urllib.parse.quote(string)
   plt.close()
   return uris

def plot_bmi_diff():
   bmis_current_year = []
   bmis_prev_year = []
   prev_year_date = datetime.now().date() - timedelta(days=365)
   prev_year = str(prev_year_date.year)
   current_year = str(datetime.now().year)
   obj = Appointment.objects.filter(date_time__contains=prev_year)
   obj1 = Appointment.objects.filter(date_time__contains=current_year)
   day_dose_diff = []
   dose_curr_y=0
   dose_prev_y=0
   for i in obj:
       prev_y_date_1 = i.date_time.strftime('%Y-%m-%d %H:%M:%S')
       prev_y_date_1=datetime.strptime(prev_y_date_1,'%Y-%m-%d %H:%M:%S')
       prev_y_date = prev_y_date_1.date()
       prev_date_comp = prev_y_date.replace(year=int(current_year))
       for j in obj1:
           curr_y_date_1 = j.date_time.strftime('%Y-%m-%d %H:%M:%S')
           curr_y_date_1 = datetime.strptime(curr_y_date_1, '%Y-%m-%d %H:%M:%S')
           curr_y_date = curr_y_date_1.date()
           if curr_y_date == prev_date_comp:
               dose_curr_y+= j.dose
               dose_prev_y+=i.dose
           else:
               if dose_curr_y>0:
                   diff = dose_curr_y - dose_prev_y
                   day_dose_diff.append(diff)
                   dose_curr_y = 0
                   dose_prev_y = 0
   print(day_dose_diff)


   #     for j in obj1:
   #         if
   #     bmis_prev_year.append(i.bmi)
   #     bmis_prev_year.append(prev_year)
   #     bmis.append(bmis_prev_year)
   #     bmis_prev_year = []
   # for i in obj1:
   #     bmis_current_year.append(i.bmi)
   #     bmis_current_year.append(current_year)
   #     bmis.append(bmis_current_year)
   #     bmis_current_year = []
   # df = pd.DataFrame(bmis, columns=["Bmis", "Year"])


   # ---------------------------------------



   #
   # plt.figure(figsize=(16, 10), dpi=80)
   # sns.kdeplot(df.loc[df['Age'] == "ages_10_20", "Bmi"], shade=True, color="g", label="ages_10_20", alpha=.7)
   # sns.kdeplot(df.loc[df['Age'] == "ages_20_30", "Bmi"], shade=True, color="deeppink", label="ages_20_30", alpha=.7)
   # sns.kdeplot(df.loc[df['Age'] == "ages_30_40", "Bmi"], shade=True, color="dodgerblue", label="ages_30_40", alpha=.7)
   # sns.kdeplot(df.loc[df['Age'] == "ages_40_50", "Bmi"], shade=True, color="orange", label="ages_40_50", alpha=.7)
   # sns.kdeplot(df.loc[df['Age'] == "ages_50_60", "Bmi"], shade=True, color="purple", label="ages_50_60", alpha=.7)
   # sns.kdeplot(df.loc[df['Age'] == "ages_60", "Bmi"], shade=True, color="#957c52", label="ages_60", alpha=.7)
   # plt.title('Density Plot of Bmi with Multiple Age Categories', fontsize=18)
   # plt.xlabel('Bmi',fontsize=15)
   # plt.ylabel('Density',fontsize=15)
   # plt.legend( title='Patients')
   # fig = plt.gcf()
   # fig.set_size_inches(18.5, 6.5)
   # buf = io.BytesIO()
   # fig.savefig(buf, format='png')
   # buf.seek(0)
   # string = base64.b64encode(buf.read())
   # uris = urllib.parse.quote(string)
   # plt.close()
   # return uris

def plot_age_bmi_violin():
   list1 = []

   ages_10_20 = Personal_information.objects.filter(age__gte=10, age__lte=20)
   ages_20_30 = Personal_information.objects.filter(age__gt=20, age__lte=30)
   ages_30_40 = Personal_information.objects.filter(age__gt=30, age__lte=40)
   ages_40_50 = Personal_information.objects.filter(age__gt=40, age__lte=50)
   ages_50_60 = Personal_information.objects.filter(age__gt=50, age__lte=60)
   ages_60 = Personal_information.objects.filter(age__gt=60)
   print(ages_10_20)
   list3 = []
   for i in ages_10_20:
       list1.append(i.bmi)
       list1.append("age_10_20")
       list1.append(i.sex)
       list3.append(list1)
       list1 = []

   for i in ages_20_30:
       list1.append(i.bmi)
       list1.append("age_20_30")
       list1.append(i.sex)
       list3.append(list1)
       list1 = []

   for i in ages_30_40:
       list1.append(i.bmi)
       list1.append("age_30_40")
       list1.append(i.sex)
       list3.append(list1)
       list1 = []

   for i in ages_40_50:
       list1.append(i.bmi)
       list1.append("age_40_50")
       list1.append(i.sex)
       list3.append(list1)
       list1 = []

   for i in ages_50_60:
       list1.append(i.bmi)
       list1.append("age_50_60")
       list1.append(i.sex)
       list3.append(list1)
       list1 = []

   for i in ages_60:
       list1.append(i.bmi)
       list1.append("age_60")
       list1.append(i.sex)
       list3.append(list1)
       list1 = []
   df = pd.DataFrame(list3, columns=["Bmi", "Age", "Sex"])

   sns.violinplot(x='Age', y='Bmi', data=df, scale='width', inner='quartile')
   sns.stripplot(x="Age", y="Bmi", color="#1a237e", data=df)
   fig = plt.gcf()
   fig.set_size_inches(18.5, 6.5)
   plt.title('Violin Plot of Bmi with Multiple Age Categories', fontsize=18)
   plt.xlabel('Age', fontsize=15)
   plt.ylabel('Bmi', fontsize=15)
   buf = io.BytesIO()
   fig.savefig(buf, format='png')
   buf.seek(0)
   string = base64.b64encode(buf.read())
   uris = urllib.parse.quote(string)
   plt.close()
   return uris


def plot_3d():
   height=[]
   weight=[]
   bmi=[]
   count = 0
   obj = Personal_information.objects.all()
   for i in obj:
       height.append(i.height)
       weight.append(i.weight)
       bmi.append(i.bmi)
   print(len(height))


   from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
   from matplotlib import cm
   from matplotlib.ticker import LinearLocator, FormatStrFormatter
   fig = plt.figure()

   ax = fig.gca(projection='3d')


   X=weight
   Y=height
   X, Y = np.meshgrid(X, Y)
   Z = X/(Y**2)
   # Plot the surface.
   surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                          linewidth=0, antialiased=False)
   # Customize the z axis.
   ax.set_xlabel("Weight(Kg)")
   ax.set_ylabel('Height (m)')
   ax.set_zlabel('Bmi')
   ttl = ax.set_title('3-D Plot of Weight, Height and Bmi of all patients', fontsize=15,)
   ttl.set_position([.5, 1.05])
   ax.set_zlim(15, 60)
   ax.zaxis.set_major_locator(LinearLocator(10))
   ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

   # Add a color bar which maps values to colors.
   fig.colorbar(surf, shrink=0.5, aspect=5)
   # for angle in range(0, 360):
   #     ax.view_init(45, angle)
   fig = plt.gcf()
   # from pylab import rcParams
   # rcParams['figure.figsize'] = 20, 10
   fig.set_size_inches(18.5, 6.5)
   buf = io.BytesIO()
   fig.savefig(buf, format='png')
   buf.seek(0)
   string = base64.b64encode(buf.read())
   uris = urllib.parse.quote(string)
   plt.close()
   return uris




def tomorrows_dose_csv(request):

   now_date = datetime.today().date()

   if now_date.weekday() == 4:
       day_tomorrow = now_date + timedelta(days=3)
   elif now_date.weekday() == 5:
       day_tomorrow = now_date + timedelta(days=2)
   else:
       day_tomorrow = now_date + timedelta(days=1)
   tomorrows_doses = Appointment.objects.filter(date_time__contains=day_tomorrow)
   total_dose = 0
   tomorrows_appointments=[]
   for i in tomorrows_doses:
       # date_time = i.date_time.strftime('%d-%m-%Y %H:%M:%S')
       app_per_pat = [i.id,i.amka_id,i.weight,i.bmi,i.dose,i.date_time]
       dose = i.dose
       total_dose = total_dose + dose
       tomorrows_appointments.append(app_per_pat)
   print(tomorrows_appointments)

   response = HttpResponse(content_type='text/csv')
   response['Content-Disposition'] = 'attachment; filename="Tomorrows_dose.csv"'
   writer = csv.writer(response)
   writer.writerow(['Appointment', 'Amka', 'Weight', 'Bmi', 'Dose', 'Date/Time'])

   for i in tomorrows_appointments:
       writer.writerow(i)
   writer.writerow([""])
   writer.writerow(["Total Dose"])
   writer.writerow([total_dose])
   return response



def tomorrows_dose_pdf(request):
   # Create the HttpResponse object with the appropriate PDF headers.
   response = HttpResponse(content_type='application/pdf')
   response['Content-Disposition'] = 'attachment; filename="Tomorrows_dose.pdf"'

   buffer = BytesIO()

   report = NextDayPrint(buffer, 'Letter')
   pdf = report.pdf_tomorrow()

   response.write(pdf)
   return response




def prev_year_csv (request):
   now_date = datetime.today().date()
   prev_year1 = now_date - timedelta(days=365)
   prev_year = prev_year1.year

   prev_year_appoints = Appointment.objects.filter(date_time__contains=prev_year)
   total_dose = 0
   total_bmi = 0
   prev_year_appointments = []
   for i in prev_year_appoints:
       app_per_pat = [i.id, i.amka_id, i.weight, i.bmi, i.dose, i.date_time]
       dose = i.dose
       total_dose = total_dose + dose
       total_bmi += i.bmi
       prev_year_appointments.append(app_per_pat)
   avg_dose = round(total_dose / len(prev_year_appoints),3)
   avg_bmi = round(total_bmi / len(prev_year_appoints),3)


   response = HttpResponse(content_type='text/csv')
   response['Content-Disposition'] = 'attachment; filename="Last Year.csv"'
   writer = csv.writer(response)
   writer.writerow(['Appointment', 'Amka', 'Weight', 'Bmi', 'Dose', 'Date/Time', ' ', ' ',  'Avg Dose:', avg_dose, ' ', 'Avg Bmi:', avg_bmi])
   # writer.writerow([' ',' ', ' ', ' ', ' ', ' ', ' ', ' ', avg_dose])
   for i in prev_year_appointments:
       writer.writerow(i)
       # writer.writerow([""])
   return response


def prev_year_pdf(request):
   response = HttpResponse(content_type='application/pdf')
   response['Content-Disposition'] = 'attachment; filename="Last_year.pdf"'

   buffer = BytesIO()

   report = PrevYearPrint(buffer, 'Letter')
   pdf = report.pdf_tomorrow()

   response.write(pdf)
   return response



















# from fpdf import FPDF
#
#
# def tomorrows_dose_pdf(request, spacing=1):
#     now_date = datetime.today().date()
#
#     if now_date.weekday() == 4:
#         day_tomorrow = now_date + timedelta(days=3)
#     else:
#         day_tomorrow = now_date + timedelta(days=1)
#     tomorrows_doses = Appointment.objects.filter(date_time__contains=day_tomorrow)
#     total_dose = 0
#     tomorrows_appointments = []
#     for i in tomorrows_doses:
#         date_time = i.date_time.strftime('%d-%m-%Y %H:%M:%S')
#         app_per_pat = [str(i.id),str(i.amka_id),str(i.weight),str(i.bmi),str(i.dose),date_time]
#         dose = i.dose
#         total_dose = total_dose + dose
#         tomorrows_appointments.append(app_per_pat)
#     data = tomorrows_appointments
#     print(data)
#
#     pdf = FPDF()
#     pdf.set_font("Arial", size=12)
#     pdf.add_page()
#
#     col_width = pdf.w / 4.5
#     row_height = pdf.font_size
#     for row in data:
#         for item in row:
#             pdf.cell(col_width, row_height*spacing,
#                      txt=item, border=1)
#         pdf.ln(row_height * spacing)
#
#
#     pdf.output(r'C:\Users\manos\Desktop\tomorrows_dose2.pdf', dest="F").encode('latin-1')
#     # pdf.output(dest='I').encode('latin-1')
#     return HttpResponse("all shit")

   # response = HttpResponse(content_type='application/pdf')
   # response['Content-Disposition'] = 'attachment; filename="tomorrows_apps.pdf"'
   # # response.write(pdf)
   # # # buffer = BytesIO
   # return response
# if __name__ == '__main__':
#     simple_table()











#
# def plot_3d():
#     count = 0
#     count1 = 0
#     two_week_total_dose_2018 = []
#     dose_per_pat_2018 = []
#     two_week_total_dose_2019 = []
#     dose_per_pat_2019 = []
#     obj = Appointment.objects.filter(date_time__contains="2019")
#
#     for i in obj:
#         dose_per_pat_2019.append(i.dose)
#         count += 1
#         if count == 80:
#             two_week_total_dose_2019.append(sum(dose_per_pat_2019))
#             dose_per_pat_2019 = []
#             count = 0
#     print(two_week_total_dose_2019)
#
#     for i in range(0,24):
#         two_week_total_dose_2018.append(24000)
#
#     print(two_week_total_dose_2018)
#
#
#
#     from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
#     from matplotlib import cm
#     from matplotlib.ticker import LinearLocator, FormatStrFormatter
#     fig = plt.figure()
#     ax = fig.gca(projection='3d')
#
#     # Make data.
#     X=np.array(two_week_total_dose_2018)
#     Y=np.array(two_week_total_dose_2019)
#     X, Y = np.meshgrid(X, Y)
#     Z=abs(Y-X)
#     X=np.arange(len(two_week_total_dose_2018))
#     Y=np.arange(len(two_week_total_dose_2019))
#
#     # Plot the surface.
#     surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
#                            linewidth=0, antialiased=False)
#
#     # Customize the z axis.
#     # ax.set_zlim(0, 10000)
#     ax.zaxis.set_major_locator(LinearLocator(10))
#     ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
#
#     # Add a color bar which maps values to colors.
#     fig.colorbar(surf, shrink=0.5, aspect=5)
#     fig = plt.gcf()
#     # from pylab import rcParams
#     # rcParams['figure.figsize'] = 20, 10
#     fig.set_size_inches(18.5, 6.5)
#     buf = io.BytesIO()
#     fig.savefig(buf, format='png')
#     buf.seek(0)
#     string = base64.b64encode(buf.read())
#     uris = urllib.parse.quote(string)
#     plt.close()
#     return uris





























   # plt.subplot(2, 1, 1)
   # plt.plot(x1, y1, '.-')
   # plt.title("Summary of dose per two weeks for Years 2019 and 2020")
   # plt.ylabel('Dose 2019')
   #
   # plt.subplot(2, 1, 2)
   # plt.plot(x2, y2, '.-')
   # plt.xlabel('15-Day')
   # plt.ylabel('Dose 2020')
   # plt.xlim(0, len(two_week_total_dose_2020))
   #
   # fig = plt.gcf()
   # # from pylab import rcParams
   # # rcParams['figure.figsize'] = 20, 10
   # fig.set_size_inches(18.5, 6.5)
   # buf = io.BytesIO()
   # fig.savefig(buf, format='png')
   # buf.seek(0)
   # string = base64.b64encode(buf.read())
   # uris = urllib.parse.quote(string)
   # plt.close()
   # return uris








   # t=np.arange(len(daily_total_dose_2019))
   # s=daily_total_dose_2019
   # fig, ax = plt.subplots()
   # ax.plot(t, s)
   #
   # ax.set(xlabel='Day of Year', ylabel='Dose',
   #        title='Dose per day for year 2019')
   # ax.grid()
   # buf = io.BytesIO()
   # fig.savefig(buf, format='png')
   # buf.seek(0)
   # string = base64.b64encode(buf.read())
   # uris = urllib.parse.quote(string)
   # plt.close()
   # return uris

