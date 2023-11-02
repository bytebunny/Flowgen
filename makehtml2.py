#!/usr/bin/env python
#### writes out HTML files. Uses .flowdbs information and .cmapx information (for hyperlinks).
#### HMTL files point to PNG files with the diagrams

import sys
import os
import glob
import csv




infile_str=os.path.splitext(os.path.basename(sys.argv[1]))[0]
print (infile_str)


htmloffline_str=''
htmloffline_str+="""<html>
    <head>
      <title>"""

htmloffline_str+=infile_str
htmloffline_str+="""</title>
      <script src="htmlCSSandJS/tabcontent.js" type="text/javascript"></script>
      <link href="htmlCSSandJS/template1/tabcontent.css" rel="stylesheet" type="text/css" />
    </head>
    
    <body>"""
 
       
#read corresponding .flowdb file (with the same filename as the argument of the call of makehtml.py)
reader = csv.reader(open('flowdoc/aux_files/'+infile_str+'.flowdb', "rt", encoding="utf8"), delimiter='\t')
#loop over annotated functions / methods
for row in reader:
  usr_key = row[0]
  usr_key = usr_key.replace('~','destructor')
  usr_key=''.join(e for e in usr_key if e.isalnum())
  
  htmloffline_str+="""
    <hr><hr><hr>"""
  htmloffline_str+="<p>"+row[2]+"</p>"+"""<a name="#"""+usr_key+""""></a>"""
  #if zoom level is 0
  if int(row[1])==0:
      zoomID=''  
      #if hyperlinks exist in the diagrams include them
      if os.path.exists('flowdoc/aux_files/'+usr_key+zoomID+'.cmapx'):
          htmloffline_str+= """
          <img src="aux_files/"""+usr_key+zoomID+""".png" """    
          map_str=open('flowdoc/aux_files/'+usr_key+zoomID+'.cmapx').read()
          htmloffline_str+=""" USEMAP="#"""+usr_key+zoomID+'_map'
          htmloffline_str+=""""/> """   
          htmloffline_str+=map_str+'\n'
      else:
          htmloffline_str+= """
          <img src="aux_files/"""+usr_key+zoomID+'.png'    
          htmloffline_str+=""" "> """
  #else, loop over zoom levels and put them into tabs
  else:
    htmloffline_str+="""
      <ul class="tabs" data-persist="true">"""
    for i in range(int(row[1])+1):
      zoomID=''
      if i>0:
        zoomID=str(i)
      if i==0:
        htmloffline_str+="""
        <li><a href="#view"""+zoomID+""" ">zoom"""+zoomID+"""</a></li>"""

      if i>0:
          for k in range (0,100):
              containerId='_'+str(k)
              # if there is a container diagram
              if os.path.exists('flowdoc/aux_files/'+usr_key+zoomID+containerId+'.png'):
                  htmloffline_str+="""
            <li><a href="#view"""+zoomID+containerId+""" ">zoom"""+zoomID+containerId+"""</a></li>"""
              else:
                  file_name = 'flowdoc/aux_files/'+usr_key+zoomID+containerId+'.png'
                  print('No container file:', file_name) 
                  break

    htmloffline_str+="""
      </ul>"""
    
    htmloffline_str+= """
      <div class="tabcontents"> """
    for i in range(int(row[1])+1):
      zoomID=''
      if i>0:
        zoomID=str(i)
      if i==0:
          htmloffline_str+="""
            <div id="view"""+zoomID+""" ">"""
          #if hyperlinks exist in the diagrams include them
          if os.path.exists('flowdoc/aux_files/'+usr_key+zoomID+'.cmapx'):
              htmloffline_str+= """<img src="aux_files/"""+usr_key+zoomID+""".png" """    
              map_str=open('flowdoc/aux_files/'+usr_key+zoomID+'.cmapx').read()
              htmloffline_str+=""" USEMAP="#"""+usr_key+zoomID+'_map'
              htmloffline_str+=""""/> """   
              htmloffline_str+=map_str+'\n'
          else:
              htmloffline_str+= """<img src="aux_files/"""+usr_key+zoomID+'.png'    
              htmloffline_str+=""" "> """
          htmloffline_str+="</div>"

      #print container diagrams
      if i>0:
          for k in range (0,100):
              containerId='_'+str(k)
              # if there is a container diagram
              if os.path.exists('flowdoc/aux_files/'+usr_key+zoomID+containerId+'.png'):
                  htmloffline_str+="""
            <div id="view"""+zoomID+containerId+""" ">"""
                  #if hyperlinks exist in the diagrams include them
                  if os.path.exists('flowdoc/aux_files/'+usr_key+zoomID+containerId+'.cmapx'):
                      htmloffline_str+= """<img src="aux_files/"""+usr_key+zoomID+containerId+""".png" """    
                      map_str=open('flowdoc/aux_files/'+usr_key+zoomID+containerId+'.cmapx').read()
                      htmloffline_str+=""" USEMAP="#"""+usr_key+zoomID+containerId+'_map'
                      htmloffline_str+=""""/> """   
                      htmloffline_str+=map_str+'\n'
                  else:
                      htmloffline_str+= """<img src="aux_files/"""+usr_key+zoomID+containerId+'.png'    
                      htmloffline_str+=""" "> """
                  htmloffline_str+="</div>"
              else:
                  break

    htmloffline_str+="""
      </div>"""
    

htmloffline_str+="""
    </body>
</html>"""
        
#write string into HTML file
writefunc = open('flowdoc/'+infile_str+'.html',"w")
writefunc.write(htmloffline_str)
writefunc.close()


