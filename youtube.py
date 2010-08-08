#youtube-dl frontend
import sys, os.path, gobject
from subprocess import *
try:  
    import pygtk  
    pygtk.require("2.0")  
except:  
    pass  
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
            "btnDefault_clicked" : self.default,
            "btnSave_clicked" : self.save_preference,
            "btnDiscard_clicked" : self.discard_changes,
        }
        
        builder.connect_signals(dic)
        # TODO: initialise the interface
        
        # TODO: load defaults for preferences
        
        # TODO: load the url list from file and create a new download file for youtube-dl
        
        # gtk.main()
        
    def quit(self,widget):
        sys.exit()        
    
    def add_url(self, widget):
        # TODO: add code to add url to list
        pass
    
    def download(self, widget):
        # TODO: add code to start download 
        # use pipe to call youtube-dl and parse output to show to gui
        utube_cmd = ["youtube-dl", "-t", "-c"]
        #get preferences
        location,vformat = self.get_pref()
        if vformat!="":
            utube_cmd.append("-f "+vformat)
        # get url
        url = self.builder.get_object("txtUrl").get_text()
        if url!="" :
            utube_cmd.append(url)
            self.file_stdout = open('utube.txt', 'w')
            self.proc = Popen(utube_cmd,  stdout=self.file_stdout, stderr=STDOUT, cwd=location)
            self.file_stdin = open('utube.txt', 'r')
            self.context_id = self.builder.get_object("statusbar").get_context_id('download status')
            self.timer = gobject.timeout_add(1000, self.download_status)
    
    def download_status(self):
        # extracts the messages from the youtube-dl execution and shows on the status bar
        msg = self.file_stdin.readline().strip()
        
        if msg != "":
            #check if msg contains "ERROR"
            if msg.count("ERROR"):
                self.builder.get_object("statusbar").push(self.context_id,msg)
                self.builder.get_object("lblProgress").set_text("Speed: --  ETA: --")
                return False # returns a false to stop polling for youtube-dl output
                
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
        try:
            self.proc.terminate()
            gobject.source_remove(self.timer)
            self.builder.get_object("statusbar").push(self.context_id,"User Abort")
            self.builder.get_object("lblProgress").set_text("Speed: --  ETA: --")
            
        except:
            pass
        
    
    def default(self, widget):
        # TODO: add code to restore defaults in the preference tab
        pass
    
    def save_preference(self, widget):
        # TODO: add code to save options in the preference tab
        # save to file and read it back
        pass
    
    def discard_changes(self, widget):
        # TODO: add code to load defaults
        pass
    
    def update_progressbar(self,percent_complete = 0):
        # TODO: add code to update progress bar as per the % complete parameter
        self.builder.get_object("progressbar").set_text(str(percent_complete)+ " %")
        self.builder.get_object("progressbar").set_fraction(percent_complete/100)
        return 

    def parse_sout(self,message):
        # TODO: add code to parse sout and return a tuple (gui_affected,value)
        pass
    
    def get_pref(self):
        # TODO: code to get preferences to be passed to youtube-dl
        # returns a tuple ('download_location','format') by default user directory and no format
        return (os.path.expanduser('~'),"")

youtubedl_gui()
gtk.main()
