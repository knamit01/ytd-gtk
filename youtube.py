#!/usr/bin/env python
#youtube-dl frontend
import sys, os.path, gobject
from subprocess import *

try:  
    import gtk  
except:  
    print("GTK Not Availible")
    sys.exit(1)

     
class youtubedl_gui:

    def __init__( self ):
        
        self.builder = gtk.Builder()
        builder = self.builder
        builder.add_from_file("youtube.xml")
        
        dic = { 
            "window_destroy" : self.quit,
            "btnAdd_clicked" : self.add_url,
            "btnCancel_clicked" : self.cancel_download,
            "btnDownload_clicked" : self.download,
            "btnSave_clicked" : self.save_preference,
            "btnDelete_clicked" : self.delete,
            "btnReload_clicked" : self.reload,
            "btnClear_clicked" : self.clear
        }
        
        builder.connect_signals(dic)
        
        # TODO: initialise the interface
        self.context_id = self.builder.get_object("statusbar").get_context_id('download status')
        
        # initialise format combo box
        vf_list = {"Default" : "",
                    "best":"-b",
                    "mobile": "-m",
                    "hi-def":"--hi-def"}
                    
        self.create_cbo_list(builder.get_object("cboFormat"),vf_list)
        
        # initialise download directory to home
        builder.get_object("folderDownload").set_current_folder(os.path.expanduser('~'))
        
        # initialise listUrl and enable multiple select
        builder.get_object("listUrl").get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
        # TODO: load the url list from file and create a new download file for youtube-dl
        
    def quit(self,widget):
        sys.exit()        
    
    def add_url(self, widget):
        # TODO: add code to add url to list
        url = self.builder.get_object("txtUrl").get_text()
        if url.strip()!="":
            self.builder.get_object("listUrl").get_model().append(["Queued",self.builder.get_object("txtUrl").get_text()])
            self.builder.get_object("txtUrl").set_text("")
        
    
    def download(self, widget):
        # Disable the download button to prevent the start of a parallel thread
        self.builder.get_object("btnDownload").set_sensitive(False)
        self.builder.get_object("vboxList").set_sensitive(False)
        # TODO: add code to start download 
        # use pipe to call youtube-dl and parse output to show to gui
        utube_cmd = ["youtube-dl", "-t", "-c"]
        
        #get preferences
        location = self.builder.get_object("folderDownload").get_current_folder()
        vformat = self.get_cbo_option(self.builder.get_object("cboFormat"))
        if vformat!="":
            utube_cmd.append(vformat)
        
		# get url
        self.current_url = self.get_next_queued() # get current_url[status,url] field
        # start download
        if self.current_url :
            utube_cmd.append(self.current_url[1]) # get url from current_url
            self.file_stdout = open('utube.txt', 'w')
            self.proc = Popen(utube_cmd,  stdout=self.file_stdout, stderr=STDOUT, cwd=location)
            self.file_stdin = open('utube.txt', 'r')
            self.current_url[0] = "Processing"
            self.timer = gobject.timeout_add(1000, self.download_status)
        else:
            # if url is empty skip download and activate download button
            self.builder.get_object("btnDownload").set_sensitive(True)
            self.builder.get_object("vboxList").set_sensitive(True)
            
    
    def download_status(self):
        # extracts the messages from the youtube-dl execution and shows on the status bar
        msg = self.file_stdin.readline().strip()
        
        if msg != "":
            #check if msg contains "ERROR"
            if msg.count("ERROR"):
                self.reset_ui("ERROR", msg)
                self.download(None)
                
            elif msg.count("[download]"):
                # extract %complete, size, speed and estimated_time
                msg = msg.split('[download]')
                msg = msg[len(msg)-1]
                dl_status = msg.split()
                if len(dl_status)>=7 :
                    dl_percent_complete = float(dl_status[0][0:-1])
                    dl_size = dl_status[2]
                    dl_speed = dl_status[4]
                    dl_time = dl_status[6]
                    self.update_progressbar(dl_percent_complete)
                    self.builder.get_object("lblProgress").set_text("Speed: "+dl_speed+" ETA: "+dl_time)
                    if dl_percent_complete >= 100.0 :
                        self.reset_ui("Done","Download complete")
                        self.download(None)
                elif dl_status[-1]=="downloaded":
                    self.reset_ui("Done","Download complete")
                    self.download(None)
                else:
                    self.builder.get_object("statusbar").push(self.context_id,msg)
            else:
                # all other messages display on status bar after removing the [xxx] entry
                msg = msg.split('] ')
                msg = msg[len(msg)-1]
                self.builder.get_object("statusbar").push(self.context_id,msg)

        return True # return is true to continue polling for output of youtube-dl
    
    def cancel_download(self, widget):
        # TODO: add code to stop downloading
        self.reset_ui("Queued","User Abort")
        
    def reload(self,widget):
        url_model, url_selected = self.builder.get_object("listUrl").get_selection().get_selected_rows()
        for url in url_selected:
            url_model[url][0] = "Queued"
    
    def delete(self,widget):
        # Delete selected items from listurl
        url_model, url_selected = self.builder.get_object("listUrl").get_selection().get_selected_rows()
        iters = [url_model.get_iter(url) for url in url_selected]
        for iter in iters:
            url_model.remove(iter)
        
    def clear(self,widget):
        # Clear listUrl
        self.builder.get_object("listUrl").get_model().clear()
    
    def reset_ui(self,url_status,status_msg):
        try:
            self.proc.terminate()
            gobject.source_remove(self.timer)
            if self.current_url:
                self.current_url[0] = url_status
            self.builder.get_object("btnDownload").set_sensitive(True)
            self.builder.get_object("vboxList").set_sensitive(True)
            self.builder.get_object("statusbar").push(self.context_id,status_msg)
            self.builder.get_object("lblProgress").set_text("Speed: --  ETA: --")
            self.builder.get_object("progressbar").set_fraction(0)
        except:
            pass
        
    
    def save_preference(self, widget):
        # TODO: add code to save options in the preference tab
        # save to file and read it back
        pass
    
    def update_progressbar(self,percent_complete = 0):
        # TODO: add code to update progress bar as per the % complete parameter
        self.builder.get_object("progressbar").set_fraction(percent_complete/100)
        return 

    def create_cbo_list(self,cbo_object,cbo_dic):
        # Create options for combo box from a dictionary
        store = gtk.ListStore(str,str)
        for item in cbo_dic:
            store.append([item,cbo_dic[item]])        
        cbo_object.set_model(store)
        cbo_object.set_active(0)
        cell = gtk.CellRendererText() 
        cbo_object.pack_start(cell) 
        cbo_object.add_attribute(cell, 'text', 0)
    
    def get_cbo_option(self,cbo_object):
        cbo_active = cbo_object.get_active()
        cbo_value = cbo_object.get_model()[cbo_active][1]
        return cbo_value
        
    def get_next_queued(self):
        url_model = self.builder.get_object("listUrl").get_model()
        for row in url_model:
            if row[0] == 'Queued':
                return row
                break
        return None

youtubedl_gui()
gtk.main()
