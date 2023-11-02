#!/usr/bin/env python
import re
import sys
import clang.cindex
import os
import glob
import csv

#colors:  http://www.color-hex.com/color/6699cc#    chosen (#84add6, #b2cce5, #e0eaf4)

##RESTRICTIONS:
#- no parallel actions 

#clang node types (CursorKind)
#8: FUNCTION_DECL
#21: CXX_METHOD
#205: IF_STMT  an if statement
#202: COMPOUND_STMT  a compound statement
#212: continue statement.
#213: A break statement.
#214: A return statement.
#207: A while statement.
#208: A do statement.
#209: A for statement.
#103: CALL_EXPR An expression that calls a function or method.
#101: DECL_REF_EXPR An expression that refers to some value declaration, such as a function, varible, or enumerator.  CursorKind.DECL_REF_EXPR = CursorKind(101)

#clang node properties
      #node.displayname: more info than .spelling
      #node.get_definition(): returns the defining node. 
      #node.location.line, node.location.column, node.location.filename
      #node.get_usr() Return the Unified Symbol Resultion (USR) for the entity referenced by the given cursor (or None).
             #A Unified Symbol Resolution (USR) is a string that identifies a particular entity (function, class, variable, etc.) within a program. USRs can be compared across translation units
      #node.get_referenced() Return the referenced object of a call
#additional feature for Cursors (nodes) that has to be added to clang python bindings
def get_referenced(self):
    return clang.cindex.conf.lib.clang_getCursorReferenced(self)

clang.cindex.Cursor.get_referenced = get_referenced

#############################################################################################
#print out a node
def print_node(context_str, node):
     node_str =' '.join(t.spelling for t in list(node.get_tokens())[0:20]) 
     print(context_str, node_str[:80])
     return

#############################################################################################
#print out a node with kind
def print_nodeK(context_str, node):
     node_str =' '.join(t.spelling for t in list(node.get_tokens())[0:20]) 
     print(context_str, node.kind.name, node_str[:80])
     return

#############################################################################################
def print_tree(nodeIN):
  def print_treeRE(nodeIN2,indent):
     indent_str=''
     for ii in range (0, indent):
        indent_str+='   '
     node_str =' '.join(t.spelling for t in list(nodeIN2.get_tokens())[0:20]) 
     print(indent_str, nodeIN2.kind.name, '=', node_str[:80])
     for d in nodeIN2.get_children(): 
        print_treeRE(d,indent+1)
  print_treeRE(nodeIN,0)
  return

#############################################################################################
#looks for an action comment inside the extent of a given node (write_zoomlevel <= diagram_zoom)
#stops at the lowest zoomlevel
def lookfor_lowestZoomactionAnnotation_inNode(nodeIN,diagram_zoom):
    
    def regexActionComment(zoom):
       if zoom==0:
          zoom=''  
       regextextActionComment_zoom=r'^\s*//\$'+str(zoom)+r'(?!\s+\[)\s+(?P<action>.+)$'
       return re.compile(regextextActionComment_zoom)       

    infile_str=nodeIN.location.file.name
    infile= open(infile_str,'r')            
    start_line=nodeIN.extent.start.line
    end_line=nodeIN.extent.end.line
    enum_file=list(enumerate(infile,start=1))      
    infile.close()
    
    #loop over zoom levels, first the lowest
    for it_zoom in range(0,diagram_zoom+1):
       #loop over source code lines
       for i, line in enum_file:
          if i in range(start_line,end_line):
             if regexActionComment(it_zoom).match(line):
                 lookfor_lowestZoomactionAnnotation_inNode.write_zoomlevel=it_zoom
                 return True   
    lookfor_lowestZoomactionAnnotation_inNode.write_zoomlevel=None
    return False

#############################################################################################
#looks up in the database generated at compilation time if a given key (function/method' USR) exists
def read_flowdbs(key):
    for file in glob.glob('flowdoc/aux_files/*.flowdb'):
       reader = csv.reader(open(file, "rt", encoding="utf8"), delimiter='\t')
       for row in reader:
          if key==row[0]:
              temp_file_str=os.path.splitext(os.path.basename(file))[0]
              read_flowdbs.file=temp_file_str
              ##read_flowdbs.zoom=row[1]
              ##read_flowdbs.displayname=row[2]
              #print (infile_str)
              #print('\n\nYEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEES\n\n')
              return True
    #print('\n\nNOOOOOOOOOEEEEEEEEEEEEEEEEEEEEEEEEEEEEE\n\n')
    return False

#############################################################################################
def read_single_flowdb(key,file):
      reader = csv.reader(open(file, "rt", encoding="utf8"), delimiter='\t')
      for row in reader:
        if key==row[0]:
            read_single_flowdb.max_diagram_zoomlevel=int(row[1])
            ##read_flowdbs.displayname=row[2]
            return True  
      return False 
        
#############################################################################################
htmlonline_str=''
write_htmlonline_firstcall=True
write_container=0


#############################################################################################
#writes out htmlonline_str adding up all the function/method's strings.
def write_htmlonline(string,outfile_str):
   global htmlonline_str
   global write_htmlonline_firstcall, write_container
   
   if write_htmlonline_firstcall: 
     htmlonline_str+="""<html><head><script type="text/javascript" src="jquery.js"></script>
     <script type="text/javascript" src="jquery_plantuml.js"></script>
     <!-- rawdeflate.js is implicity used by jquery_plantuml.js --></head>"""+'\n'+"""<body><hr>"""
     htmlonline_str+="<p>"+outfile_str+"</p>"
     htmlonline_str+= """<img uml=" """+string
     htmlonline_str+= """ "></body></html>"""
     
     write_htmlonline_firstcall=False
     write_container=0
   else:
     htmlonline_str =htmlonline_str[:-14]
     htmlonline_str+="<hr><p>"+outfile_str+"</p>"
     htmlonline_str+= """<img uml=" """+string
     htmlonline_str+= """ "></body></html>"""
        
   return

#############################################################################################
#writes each diagram separately into a plantuml .txt file
def write_txt(string,outfile_str):
   f = open('flowdoc/aux_files/'+outfile_str+".txt","w")
   f.write(string)
   f.close()
   return

#############################################################################################
#writes a container diagram separately into a plantuml .txt file
def write_txt_container(string,outfile_str):
   global write_container   
   myoutfile_str =outfile_str+"_"+str(write_container)
   f = open('flowdoc/aux_files/'+myoutfile_str+".txt","w")

   mystring='@startuml\n\nstart\n skinparam activityBackgroundColor #white \n'
   mystring+=string
   mystring+='\nstop\n@enduml'
   f.write(mystring)
   f.close()
        
   #write_htmlonline(mystring,myoutfile_str)
   write_container+=1
   return

   
#############################################################################################
#finds calls in a source code line that has been annotated with //$ at the end
#call nodes are only associated to the characters '(' ',' ')' of the source code line 
#there can also be variables whose definition involves a call. These kind of calls are also picked up.
#several different calls in the same line can be identified. 
#TO DO: identify calls inside other calls!
#CXXMemberCallExpr: call to a member method
#CallExpr: call to a function
def find_calls(scan_fileIN,scan_lineIN,scan_column_startIN,scan_column_endIN):

  singlelinecallsdefArrayIN=[]
    
  for it in range(scan_column_startIN,scan_column_endIN):
     
    loc=clang.cindex.SourceLocation.from_position(tu,scan_fileIN,scan_lineIN,it)
    scan_node=clang.cindex.Cursor.from_location(tu,loc)
    #print('position',it,'scannode ',scan_node.kind.name)    
    #call or variable found?
    #DECL_REF_EXPR (101) is an expression that refers to some value declaration, such as a function, variable, or enumerator (use node.get_referenced())
    referencefound = (scan_node.kind.name=='DECL_REF_EXPR')
    #CALL_EXPR (103) is a call
    callfound = (scan_node.kind.name=='CALL_EXPR')

    #DECL_REF_EXPR (101) --> we look for its definition (in the same source file!), it should be a VAR_DECL (9) --> we look for its children, there should be a CALL_EXPR (103)
    if referencefound and scan_node.get_definition():
      #print ('reference found')
      if scan_node.get_definition().kind.name == 'VAR_DECL': 
        #print ('scannode.getdefinition is VAR_DECL')       
        for it9 in scan_node.get_definition().get_children():
           #print ('scan_node.get_definition().get_children() ',it9.kind.name)
           if it9.kind.value==103:
              if it9.get_definition() not in singlelinecallsdefArrayIN:
                   singlelinecallsdefArrayIN.append(it9.get_definition())
    
    #CALL_EXPR (103) is a call  --> it is better to use the node_call.get_referenced() but this may not be defined (we throw a WARNING in this case)
    #Note: apparently node_call.get_definition() is not defined.                 
    elif callfound:        
        #print ('call found')
        if scan_node not in singlelinecallsdefArrayIN:
           if scan_node.get_referenced():  
              singlelinecallsdefArrayIN.append(scan_node.get_referenced())
              #print ('registered call: getreferenced ',scan_node.get_referenced().kind.name, scan_node.get_referenced().displayname, 'USR', scan_node.get_referenced().get_usr())
              #print ('registered call: getdefinition ',scan_node.get_definition().kind.name, scan_node.get_definition().displayname, 'USR')              
           else:
              print ('WARNING ',scan_node.spelling, ": No get_referenced for the cursor")
              singlelinecallsdefArrayIN.append(scan_node)             
              #print ('registered call:', scan_node.kind.name, scan_node.extent, scan_node.displayname, 'USR', scan_node.get_usr())
   
  return singlelinecallsdefArrayIN  
  
#############################################################################################
#main process function
def process_find_functions(node,MAX_diagram_zoomlevel):
      global write_container
      #\s --> [ \t\r\f\v] : avoids newlines \n 
      # (?! ): negative lookahead
      # ()?: optional group

      #############################################################################################
      def regexActionComment(zoom):
         if zoom==0:
            zoom=''  
         regextextActionComment_zoom=r'^\s*//\$'+str(zoom)+r'(?!\s+\[)\s+(?P<action>.+)$'
         return re.compile(regextextActionComment_zoom)    
            
      #############################################################################################
      def regexContextualComment(zoom):
         if zoom==0:
            zoom=''  
         regextextActionComment_zoom=r'^\s*//\$'+str(zoom)+r'\s+\[(?P<condition>.+)\]\s*$'
         return re.compile(regextextActionComment_zoom)    

      #############################################################################################
      # regexContextualComment = re.compile(r'^\s*//\$\s+\[(?P<condition>.+)\]\s*$')
      regexHighlightComment = re.compile(r'^\s*(?P<commandline>.+?)\s+//\$\s*(?:$|//.+$)') 

      start_line= node.extent.start.line
      end_line= node.extent.end.line     
      infile_clang=node.location.file
      global infile_str
      infile_str=node.location.file.name
      infile= open(infile_str,'r')            
      #lines enumerated starting from 1
      enum_file=list(enumerate(infile,start=1))      
      infile.close()
    
      print ('Processing %s of kind %s [start_line=%s, end_line=%s. At "%s"]' % (
                                            node.spelling, node.kind.name , node.extent.start.line, node.extent.end.line, node.location.file))

      #TO DO: zoom loop generates all possible zoom levels. Instead, only relevant zoom for each diagram should be generated.       
      zoom_str_Array=['','1','2','3']
      for diagram_zoomlevel in range(0,MAX_diagram_zoomlevel+1):
                    
        class_name=''
        if node.kind.name=='CXX_METHOD' or node.kind.name=='CONSTRUCTOR' or node.kind.name=='DESTRUCTOR':           
          class_name=str(node.semantic_parent.spelling)+'_'
          #also see node.lexical_parent.spelling
        outfile_str = str(node.get_usr())+zoom_str_Array[diagram_zoomlevel]
        #remove special characters from outfile_str 
        if node.kind.name=='DESTRUCTOR':
           outfile_str = outfile_str.replace('~','destructor')
        outfile_str = ''.join(e for e in outfile_str if e.isalnum())
        #outfile= open(outfile_str+'.txt', "w+")  

        
        #############################################################################################
        def increase_depthlevel():
           nonlocal depthlevel
           depthlevel+=1
           write_strings(write_zoomlevel)
           return 

        #############################################################################################
        def decrease_depthlevel():
           nonlocal flagparallelactions, depthlevel, string, indentation_level
           depthlevel-=1
           write_strings(write_zoomlevel)
           ##if activated parallelflag
           #if flagparallelactions[0]==True and depthlevel==flagparallelactions[1]:
           #   string+= indentation_level*tab+'end fork\n' 
           #   flagparallelactions[0]=False
           #   flagparallelactions[1]=None 
           return      
           
        #############################################################################################
        #taken from http://stackoverflow.com/questions/2657693/insert-a-newline-character-every-64-characters-using-python           
        #def insert_newlines(string, every=75):
        #    lines = []
        #    for i in range(0, len(string), every):
        #       lines.append(string[i:i+every])
        #    return '\n'.join(lines)     
        
        #############################################################################################
        def color(zoomlevel_IN):
           if zoomlevel_IN==0:
              return '#84add6'
           elif zoomlevel_IN==1:
              return '#b2cce5'
           elif zoomlevel_IN==2:
              return '#e0eaf4'
           elif zoomlevel_IN==3:
              return '#46ebcd'
                           
        #############################################################################################
        #other variables
        depthlevel=0
        #flagparallelactions=(flag TRUE/FALSE,depthlevel)
        flagparallelactions=[False,0]
        lastcommentlinematched=[0,0,0,0]
        tab='   '
        indentation_level=0
        last_comment_str=["","","",""]
        string_notes=["","","",""]
        string=''
        string_tmp=["","","",""]
        inside_comment_flag=[False,False,False,False]
        actioncallsdefArray=[]
        write_zoomlevel=None
        returnFound=False

        #for handling switch statements
        switchVar=''
        caseLevel=0
        caseNumber=0
        caseConditionStr=''
        caseDescription=None
        noIfForCase = False
        breakContext=''
        caseContext=''
        
        #############################################################################################
        def write_strings(write_zoomlevelMIN):
          nonlocal string, string_tmp, diagram_zoomlevel
          write_zoomlevelMAX=-100  #initialize variable to absurd value
          #write_zoomlevelMIN: the MIN zoomlevel annotations that will be written. Specified as an entry to the function.
          #write_zoomlevelMAX: the MAX zoomlevel annotations that will be written. Found out inside this function.
          #diagram_zoomlevel: the diagram zoomlevel. write_zoomlevelMAX is lower or equal.
              
          #############################################################################################
          def write_string_container(write_zoomlevelIN):
            nonlocal string_tmp,last_comment_str, inside_comment_flag, diagram_zoomlevel
            header_txt = last_comment_str[write_zoomlevelIN]
            header_txt = header_txt.replace('|','')
            body_txt = string_tmp[write_zoomlevelIN+1]
            partition_txt = indentation_level*tab+'partition '+color(write_zoomlevelIN)+' "'+ header_txt+'" {\n'+ body_txt +indentation_level*tab+'}\n'
                 
            string_tmp[write_zoomlevelIN] += partition_txt
            last_comment_str[write_zoomlevelIN]=""
            inside_comment_flag[write_zoomlevelIN]=False
            if ('partition #' not in body_txt) and (write_zoomlevelIN+1 == diagram_zoomlevel):
               write_txt_container(partition_txt, outfile_str)
            string_tmp[write_zoomlevelIN+1]=""
            return #write_string_container
          
          #############################################################################################
          def write_string_normal(write_zoomlevelIN):
             nonlocal string_notes
             nonlocal string_tmp
             nonlocal last_comment_str
             nonlocal inside_comment_flag
             nonlocal actioncallsdefArray
             if inside_comment_flag[write_zoomlevelIN]:
                #write action comment
                if last_comment_str[write_zoomlevelIN].endswith('}'):
                   isPartitionHeader = False
                   last_comment_str[write_zoomlevelIN]=indentation_level*tab+':'+color(write_zoomlevelIN)+':'+last_comment_str[write_zoomlevelIN]+'\n'   
                elif last_comment_str[write_zoomlevelIN].endswith('|'):
                   isPartitionHeader = True
                   last_comment_str[write_zoomlevelIN]=indentation_level*tab+':'+color(write_zoomlevelIN)+':'+last_comment_str[write_zoomlevelIN]+'\n'   
                else:
                   isPartitionHeader = False
                   last_comment_str[write_zoomlevelIN]=indentation_level*tab+':'+color(write_zoomlevelIN)+':'+last_comment_str[write_zoomlevelIN]+';\n'   
                #write extra if there are calls
                if actioncallsdefArray:
                   last_comment_str[write_zoomlevelIN]=last_comment_str[write_zoomlevelIN][:-2]+"\n----"
                   for it7 in actioncallsdefArray:
                      usr_id_str= str(it7.get_usr())
                      usr_id_str = ''.join(e for e in usr_id_str if e.isalnum())
                      classname = ''
                      if it7.kind.name=='CXX_METHOD' or it7.kind.name=='CONSTRUCTOR' or node.kind.name=='DESTRUCTOR':
                        classname= str(it7.semantic_parent.spelling)+'::\n'  
                      funcName = str(it7.displayname)
                      funcName = funcName.replace(',',',\n   ')                    
                      if read_flowdbs(it7.get_usr()):
                        call_in_filename_str=read_flowdbs.file+'.html'
                        last_comment_str[write_zoomlevelIN]+='\n'+str(it7.result_type.kind.name)+' '+classname+funcName+' -- [['+call_in_filename_str+'#'+usr_id_str+' link]]'
                      else:
                        last_comment_str[write_zoomlevelIN]+='\n'+str(it7.result_type.kind.name)+' '+classname+funcName
                        
                        #last_comment_str+=str(it7.result_type.kind.name)+' '+str()+str(it7.displayname)+' -- [[http://www.google.es]]'+'\\n'
                   if isPartitionHeader:
                      last_comment_str[write_zoomlevelIN]+='|\n'
                   else:
                      last_comment_str[write_zoomlevelIN]+=';\n'
                #write extra if there are notes
                if string_notes[write_zoomlevelIN] != "":
                   last_comment_str[write_zoomlevelIN]+= "note right\n"+string_notes[write_zoomlevelIN]+"end note\n"
                   string_notes[write_zoomlevelIN]=""
                #write in temporal string
                string_tmp[write_zoomlevelIN]+=last_comment_str[write_zoomlevelIN]
                last_comment_str[write_zoomlevelIN]='' 
                #reinitialize flags             
                inside_comment_flag[write_zoomlevelIN]=False
                actioncallsdefArray=[]
             return #write_string_normal
          
          #############################################################################################
          #reverse loop to find write_zoomlevelMAX and call write_string_normal(write_zoomlevelMAX) if necessary
          for zoom_it in range(diagram_zoomlevel,write_zoomlevelMIN-1,-1):
            #annotation exists at this level and is not written in temporal string yet
            if inside_comment_flag[zoom_it]:
              write_zoomlevelMAX=zoom_it
              write_string_normal(write_zoomlevelMAX)
              break
            #the temporal string exists at this level
            elif string_tmp[zoom_it] != "": 
              write_zoomlevelMAX=zoom_it
              break
          
          #reverse loop from ( write_zoomlevelMAX - 1 ) to write_zoomlevelMIN, where write_string_container() is called
          for zoom_it2 in range(write_zoomlevelMAX-1,write_zoomlevelMIN-1,-1):
            write_string_container(zoom_it2)

             
          #if zoomlevelMIN=0 write temporal string to main string
          if write_zoomlevelMIN==0:
            string+=string_tmp[0]
            string_tmp[0]='' 
          
          return #write_strings          
            
          ##write last action annotations for current zoom level and all possible higher ones in their corresponding temporal string
          #for zoom_it in range(write_zoomlevelMIN, diagram_zoomlevel+1):
          #   write_string_normal(zoom_it)
          ##write temporal strings of higher level zooms in the current zoomlevel temporal string
          #for zoom_it2 in range(write_zoomlevelMIN+1,diagram_zoomlevel+1):
          #   string_tmp[write_zoomlevelMIN]+=string_tmp[zoom_it2] 
          #   string_tmp[zoom_it2]=''
             
       
        #############################################################################################
        # procedures for processing nodes
        #############################################################################################
        def process_call_expr_node(node, last_line):
           nonlocal actioncallsdefArray
           new_last_line = last_line
           regexHighlightComment = re.compile(r'^\s*(?P<commandline>.+?)\s+//\$\s*(?:$|//.+$)') 
           highlight = None  
           line=''

           for i in range(node.extent.start.line,node.extent.end.line+1):
              line = enum_file[i-1][1]
              line_highlight = regexHighlightComment.match(line)
              if line_highlight != None:
                 highlight = line_highlight
                 break

           if highlight:
              print ('LOOKING FOR CALLS')
              ref_node = node.get_referenced()
              if ref_node:
                 if ref_node not in actioncallsdefArray:
                     actioncallsdefArray.append(ref_node)
                     #print_node('Added ', ref_node)

           return new_last_line#process_call_expr_node

        #############################################################################################
        def process_del_expr_node(node, last_line):
           nonlocal actioncallsdefArray
           new_last_line = last_line
           regexHighlightComment = re.compile(r'^\s*(?P<commandline>.+?)\s+//\$\s*(?:$|//.+$)') 
           highlight = None  
           line=''

           for i in range(node.extent.start.line,node.extent.end.line+1):
              line = enum_file[i-1][1]
              line_highlight = regexHighlightComment.match(line)
              if line_highlight != None:
                 highlight = line_highlight
                 break

           if highlight:
              print ('LOOKING FOR CALLS')
              print_nodeK('DELETE Node',node)

              # Todo: find corresponding destructor node

              #
              #  if ref_node not in actioncallsdefArray:
              #      actioncallsdefArray.append(ref_node)
                     #print_node('Added ', ref_node)

           return new_last_line#process_del_expr_node


        #############################################################################################
        def process_decl_ref_expr(node, last_line):
           nonlocal actioncallsdefArray
           new_last_line = last_line
           regexHighlightComment = re.compile(r'^\s*(?P<commandline>.+?)\s+//\$\s*(?:$|//.+$)') 
           highlight = None  
           line=''
           
           for i in range(node.extent.start.line,node.extent.end.line+1):
              line = enum_file[i-1][1]
              line_highlight = regexHighlightComment.match(line)
              if line_highlight != None:
                 highlight = line_highlight
                 break

           if highlight:
              print ('LOOKING FOR CALLS')
              ref_node = node.get_definition()
              if ref_node:
                 #print('node.get_definition() is not none')
                 if ref_node.kind.name == 'VAR_DECL': 
                     #print_nodeK('     ',ref_node)
                     for e in ref_node.get_children():
                         #print_nodeK('     child',e)
                         if e.kind.name == 'CALL_EXPR':
                            ref_node = e.get_definition()
                            if ref_node not in actioncallsdefArray:
                               actioncallsdefArray.append(ref_node)
                               #print_node('Added ', ref_node)

           return new_last_line #process_decl_ref_expr

        #############################################################################################
        def process_compound_stmt(node, last_line):
           nonlocal write_zoomlevel
           new_last_line = last_line
           if lookfor_lowestZoomactionAnnotation_inNode(node,diagram_zoomlevel):
              #adjust zoomlevel
              my_write_zoomlevel=lookfor_lowestZoomactionAnnotation_inNode.write_zoomlevel
              write_zoomlevel=my_write_zoomlevel
              for e in node.get_children():
                 new_last_line = process_node(e, new_last_line)
                 write_zoomlevel=my_write_zoomlevel
           return new_last_line #process_compound_stmt

        #############################################################################################
        def process_method(node, last_line):
           nonlocal write_zoomlevel, returnFound
           new_last_line = last_line
           returnFound = False
           if lookfor_lowestZoomactionAnnotation_inNode(node,diagram_zoomlevel):
              #adjust zoomlevel
              my_write_zoomlevel=lookfor_lowestZoomactionAnnotation_inNode.write_zoomlevel
              write_zoomlevel=my_write_zoomlevel
              for e in node.get_children():
                 new_last_line = process_node(e, new_last_line)
                 write_zoomlevel=my_write_zoomlevel

              if not returnFound:
                 write_strings(write_zoomlevel)
                 string_tmp[write_zoomlevel]+= "\nstop\n"

           return new_last_line #process_compound_stmt

        #############################################################################################
        def process_if_stmt(node, last_line):
           nonlocal diagram_zoomlevel, write_zoomlevel, regexContextualComment, string_tmp, indentation_level
           new_last_line = last_line
           ifstmt_write_zoomlevel = -1

           if lookfor_lowestZoomactionAnnotation_inNode(node,diagram_zoomlevel):
              #adjust zoomlevel
              ifstmt_write_zoomlevel=lookfor_lowestZoomactionAnnotation_inNode.write_zoomlevel
              write_zoomlevel=ifstmt_write_zoomlevel
              #increase depthlevel
              increase_depthlevel()
              #write 'if' in string
              i = node.extent.start.line
              description = regexContextualComment(write_zoomlevel).match(enum_file[i-1-1][1])
              if description:
                 string_tmp[write_zoomlevel]+= '\n'+  indentation_level*tab + 'if ('+description.group('condition')+') then(yes)''\n'
              else:                         
                 string_condition=' '.join(t.spelling for t in list(node.get_children())[0].get_tokens()) 
                 string_condition=string_condition[:-1]
                 string_tmp[write_zoomlevel]+= '\n'+  indentation_level*tab + 'if ('+string_condition+' ?) then(yes)''\n'
              #mark } endif to be written in string
              indentation_level+=1

              counter = 0
              for e in node.get_children():
                  if (e.kind.name != 'BINARY_OPERATOR') and (e.kind.name != 'UNARY_OPERATOR') and (e.kind.name != 'UNEXPOSED_EXPR'):
                     counter+=1
                     if counter == 2:
                           #begin of else block
                           decrease_depthlevel()
                           increase_depthlevel()
                           #write 'else' in string
                           string_tmp[write_zoomlevel]+= (indentation_level-1)*tab+'else(no)'+'\n' 
                  new_last_line = process_node(e, new_last_line)
                  write_zoomlevel=ifstmt_write_zoomlevel
               
              #end of if statement    
              write_zoomlevel=ifstmt_write_zoomlevel
              decrease_depthlevel()                   
              #is the else condition explicitly written? Otherwise write now
              if counter == 1:
                string_tmp[write_zoomlevel]+= (indentation_level-1)*tab+'else(no)'+'\n'
              #write endif's in string
              string_tmp[write_zoomlevel]+= (indentation_level-1)*tab +'endif'+'\n'+'\n'
              indentation_level-=1    

           return new_last_line #process_if_stmt

        #############################################################################################
        def process_case_stmt(node, last_line):
           nonlocal switchVar, caseLevel, caseNumber, write_zoomlevel, string_tmp, indentation_level
           nonlocal caseConditionStr, regexContextualComment, caseDescription, noIfForCase, caseContext
           new_last_line = last_line

           caseConditionStrIN=''
           descriptionIN=None
           caseNumberIN=caseNumber
           switchVarIN = switchVar

           if lookfor_lowestZoomactionAnnotation_inNode(node,diagram_zoomlevel):
               #adjust zoomlevel
               my_write_zoomlevel=lookfor_lowestZoomactionAnnotation_inNode.write_zoomlevel
               write_zoomlevel=my_write_zoomlevel

               if caseLevel == 0:
                  caseConditionStr=''
                  i = node.extent.start.line
                  descriptionIN = regexContextualComment(write_zoomlevel).match(enum_file[i-1-1][1])
                  if descriptionIN:
                     caseConditionStrIN=descriptionIN
                     caseDescription=descriptionIN
               else:
                  descriptionIN = caseDescription

               counter = 0
               for e in node.get_children():
                  if not descriptionIN:
                     if caseConditionStrIN =='':
                         caseConditionStrIN = ' '.join(t.spelling for t in e.get_tokens())
                         caseConditionStrIN ='( ' + switchVar + ' == ' + caseConditionStrIN + ')'
                         if caseConditionStr != '':
                             caseConditionStrIN= caseConditionStr + ' or ' + caseConditionStrIN

                  # first child = condition
                  # second child = first statement
                  counter+=1
                  if (counter >= 2) and (e.kind.name != 'CASE_STMT') and (e.kind.name != 'NULL_STMT'): 
                      if descriptionIN:
                         condition = descriptionIN.group('condition')
                      else:                         
                         condition = caseConditionStrIN

                      if caseContext == 'BIGSWITCH_STMT':
                         if caseNumberIN == 1:
                             string_tmp[write_zoomlevel]+= '\n'+  indentation_level*tab + 'split\n'
                         else:
                             string_tmp[write_zoomlevel]+= '\n'+  indentation_level*tab + 'split again\n'
                         indentation_level+=1
                         write_strings(write_zoomlevel)
                         inside_comment_flag[write_zoomlevel]=True
                         last_comment_str[write_zoomlevel] += condition + '}'
                         lastcommentlinematched[write_zoomlevel] = e.extent.start.line                           
                      else:
                          if noIfForCase:
                             write_strings(write_zoomlevel)
                             inside_comment_flag[write_zoomlevel]=True
                             last_comment_str[write_zoomlevel] += condition
                             lastcommentlinematched[write_zoomlevel] = e.extent.start.line 
                          else:
                            string_tmp[write_zoomlevel]+= '\n'+  indentation_level*tab + 'if ('+condition+') then(yes)''\n'
                            indentation_level+=1
                  
                  #set parameters for next case
                  caseLevel+=1
                  caseDescription = descriptionIN
                  caseNumber= caseNumberIN
                  switchVar = switchVarIN
                  caseConditionStr = caseConditionStrIN
                  new_last_line = process_node(e, new_last_line)
                  write_zoomlevel=my_write_zoomlevel
           
           return new_last_line #process_case_stmt

        #############################################################################################
        def process_default_stmt(node, last_line):
           nonlocal switchVar, caseLevel, caseNumber, write_zoomlevel, string_tmp, indentation_level
           nonlocal caseConditionStr, regexContextualComment, caseDescription, noIfForCase, caseContext
           new_last_line = last_line

           caseConditionStrIN=''
           descriptionIN=None
           caseNumberIN=caseNumber
           switchVarIN = switchVar

           if lookfor_lowestZoomactionAnnotation_inNode(node,diagram_zoomlevel):
               #adjust zoomlevel
               my_write_zoomlevel=lookfor_lowestZoomactionAnnotation_inNode.write_zoomlevel
               write_zoomlevel=my_write_zoomlevel

               if caseLevel == 0:
                  caseConditionStr=''
                  i = node.extent.start.line
                  descriptionIN = regexContextualComment(write_zoomlevel).match(enum_file[i-1-1][1])
                  if descriptionIN:
                     caseConditionStrIN=descriptionIN
                     caseDescription=descriptionIN
               else:
                  descriptionIN = caseDescription

               counter = 0
               for e in node.get_children():
                  if not descriptionIN:
                     if caseConditionStrIN =='':
                         caseConditionStrIN ='( ' + switchVar + ' is other value)'
                         if caseConditionStr != '':
                             caseConditionStrIN= caseConditionStr + ' or ' + caseConditionStrIN

                  # first child = first statement
                  counter+=1
                  if (counter >= 1) and (e.kind.name != 'CASE_STMT') and (e.kind.name != 'NULL_STMT'): 
                      if descriptionIN:
                         condition = descriptionIN.group('condition')
                      else:                         
                         condition = caseConditionStrIN

                      if caseContext == 'BIGSWITCH_STMT':
                         if caseNumberIN == 1:
                             string_tmp[write_zoomlevel]+= '\n'+  indentation_level*tab + 'split\n'
                         else:
                             string_tmp[write_zoomlevel]+= '\n'+  indentation_level*tab + 'split again\n'
                         indentation_level+=1
                         write_strings(write_zoomlevel)
                         inside_comment_flag[write_zoomlevel]=True
                         last_comment_str[write_zoomlevel] += condition + '}'
                         lastcommentlinematched[write_zoomlevel] = e.extent.start.line                           
                      else:
                          if noIfForCase:
                             write_strings(write_zoomlevel)
                             inside_comment_flag[write_zoomlevel]=True
                             last_comment_str[write_zoomlevel] += condition
                             lastcommentlinematched[write_zoomlevel] = e.extent.start.line 
                          else:
                            string_tmp[write_zoomlevel]+= '\n'+  indentation_level*tab + 'if ('+condition+') then(yes)''\n'
                            indentation_level+=1
                  
                  #set parameters for next case level
                  caseLevel+=1
                  caseDescription = descriptionIN
                  caseNumber= caseNumberIN
                  switchVar = switchVarIN
                  caseConditionStr = caseConditionStrIN
                  new_last_line = process_node(e, new_last_line)
                  write_zoomlevel=my_write_zoomlevel
           return new_last_line #process_default_stmt

        #############################################################################################
        def process_switch_stmt(node, last_line):
           nonlocal switchVar, caseLevel, caseNumber, write_zoomlevel, string_tmp, indentation_level
           nonlocal breakContext, caseContext, noIfForCase
           new_last_line = last_line
           defaultFound = False
           lastCase = 0
           lastCompoundChild = 0

           switchVarIN=''
           switch_write_zoom_level=-1

           write_strings(write_zoomlevel)

           if lookfor_lowestZoomactionAnnotation_inNode(node,diagram_zoomlevel):
                #adjust zoomlevel
                switch_write_zoom_level=lookfor_lowestZoomactionAnnotation_inNode.write_zoomlevel
                write_zoomlevel=switch_write_zoom_level

                caseNumberIN=0
                for e in node.get_children():
                   if switchVarIN == '':
                      switchVarIN = ' '.join(t.spelling for t in e.get_tokens())
                   if e.kind.name == 'COMPOUND_STMT':
                      #do some preporcessing
                      i = 0
                      for f in e.get_children():
                         i+=1
                         if f.kind.name == 'DEFAULT_STMT':
                             defaultFound = True
                         if (f.kind.name == 'CASE_STMT') or (f.kind.name == 'DEFAULT_STMT'):
                             lastCase = i
                             caseNumberIN+=1
                      lastCompoundChild = i

                      if caseNumberIN <= 8:
                      #----------------------------------------------------------------------- 
                          i = 0
                          caseNumberIN=0
                          for f in e.get_children():
                             i+=1
                             
                             if (i == lastCompoundChild):
                                 # Do not process last break statement
                                 breakContext='' 
                             else:
                                 breakContext='SWITCH_STMT'

                             if (f.kind.name == 'CASE_STMT') or (f.kind.name == 'DEFAULT_STMT'):
                                 #set parameters for call
                                 caseNumberIN+=1
                                 switchVar = switchVarIN
                                 caseLevel=0
                                 caseNumber = caseNumberIN
                                 if (i == lastCase) and (defaultFound):
                                    noIfForCase = True
                                 else:                        
                                    noIfForCase = False
                             
                             caseContext ='SWITCH_STMT'
                             new_last_line = process_node(f, new_last_line)
                             write_zoomlevel = switch_write_zoom_level

                          # terminate with empty else branch if no default found or only 1 case
                          if not defaultFound:
                             decrease_depthlevel() 
                             #write last else in string                  
                             string_tmp[write_zoomlevel]+= (indentation_level-1)*tab+'else(no)'+'\n'
                          else:
                             caseNumberIN-=1

                          write_strings(switch_write_zoom_level)
                          for i in range (0, caseNumberIN):
                             #write endif's in string
                             string_tmp[write_zoomlevel]+= (indentation_level-1)*tab +'endif'+'\n'+'\n'
                             indentation_level-=1  
                      else:
                      #----------------------------------------------------------------
                          i = 0
                          caseNumberIN=0
                          for f in e.get_children():
                             i+=1
                             if (f.kind.name == 'BREAK_STMT'):
                                if (i == lastCompoundChild):
                                   #do not process last break statement
                                   break

                             if (f.kind.name == 'CASE_STMT') or (f.kind.name == 'DEFAULT_STMT'):
                                 #set parameters for call
                                 caseNumberIN+=1
                                 switchVar = switchVarIN
                                 caseLevel=0
                                 caseNumber = caseNumberIN
                             breakContext='BIGSWITCH_STMT'
                             caseContext ='BIGSWITCH_STMT'
                             new_last_line = process_node(f, new_last_line)
                             write_zoomlevel = switch_write_zoom_level

                           
                          # terminate with empty else branch if no default found or only 1 case
                          if not defaultFound:
                             decrease_depthlevel()                             
                             string_tmp[write_zoomlevel]+= (indentation_level-1)*tab+'split again\n'                             
                             increase_depthlevel() 
                             inside_comment_flag[write_zoomlevel]=True
                             last_comment_str[write_zoomlevel] += 'Other values}'
                             lastcommentlinematched[write_zoomlevel] = e.extent.start.line 

                          write_strings(write_zoomlevel)
                          decrease_depthlevel()
                          string_tmp[write_zoomlevel]+= (indentation_level-1)*tab +'end split\n\n'

                   else:   
                      new_last_line = process_node(e, new_last_line)
           
           return new_last_line #process_decl_switch_stmt

        #############################################################################################
        def process_while_stmt(node, last_line):
           nonlocal diagram_zoomlevel, inside_comment_flag, last_comment_str, lastcommentlinematched
           nonlocal string_tmp, indentation_level
           nonlocal breakContext
           new_last_line = last_line

           if lookfor_lowestZoomactionAnnotation_inNode(node,diagram_zoomlevel):
              #adjust zoomlevel
              my_write_zoomlevel=lookfor_lowestZoomactionAnnotation_inNode.write_zoomlevel
              write_zoomlevel=my_write_zoomlevel

              i = node.extent.start.line
              description = regexContextualComment(write_zoomlevel).match(enum_file[i-1-1][1])
              
              counter = 0
              for e in node.get_children():
                 counter+=1
              
                 if counter == 1: # the condition
                    if description:
                       text = description.group('condition')
                    else:
                       text = ' '.join(t.spelling for t in e.get_tokens())
                    write_strings(write_zoomlevel)
                    string_tmp[write_zoomlevel]+= '\n'+  indentation_level*tab + 'while ('+text+')''\n'
                    indentation_level+=1

                 if counter == 2: #process the body
                     breakContext='WHILE_STMT'
                     new_last_line = process_node(e, new_last_line)

              write_zoomlevel=my_write_zoomlevel
              decrease_depthlevel()                   
              string_tmp[write_zoomlevel]+= (indentation_level-1)*tab +'endwhile'+'\n'+'\n'
              indentation_level-=1  

           return new_last_line #process_while_stmt

        #############################################################################################
        def process_do_stmt(node, last_line):
           nonlocal diagram_zoomlevel, inside_comment_flag, last_comment_str, lastcommentlinematched
           nonlocal string_tmp, indentation_level
           nonlocal breakContext
           new_last_line = last_line

           if lookfor_lowestZoomactionAnnotation_inNode(node,diagram_zoomlevel):
              #adjust zoomlevel
              my_write_zoomlevel=lookfor_lowestZoomactionAnnotation_inNode.write_zoomlevel
              write_zoomlevel=my_write_zoomlevel

              i = node.extent.end.line
              description = regexContextualComment(write_zoomlevel).match(enum_file[i-1-1][1])
              
              counter = 0
              for e in node.get_children():
                 counter+=1
              
                 if counter == 1: #process the body
                    write_strings(write_zoomlevel)
                    string_tmp[write_zoomlevel]+= '\n'+  indentation_level*tab + 'repeat''\n'
                    indentation_level+=1
                    breakContext='DO_STMT'
                    new_last_line = process_node(e, new_last_line)
                    write_zoomlevel=my_write_zoomlevel
                    decrease_depthlevel() 

                 if counter == 2: # the condition
                    if description:
                       text = description.group('condition')
                    else:
                       text = ' '.join(t.spelling for t in e.get_tokens())
                    write_strings(write_zoomlevel)
                    string_tmp[write_zoomlevel]+= '\n'+  indentation_level*tab + 'repeat while ('+text+')''\n'

              indentation_level-=1  

           return new_last_line #process_do_stmt

        #############################################################################################
        def process_for_stmt(node, last_line):
           nonlocal diagram_zoomlevel, inside_comment_flag, last_comment_str, lastcommentlinematched
           nonlocal string_tmp, indentation_level
           nonlocal breakContext
           new_last_line = last_line

           if lookfor_lowestZoomactionAnnotation_inNode(node,diagram_zoomlevel):
              #adjust zoomlevel
              for_write_zoom_level=lookfor_lowestZoomactionAnnotation_inNode.write_zoomlevel
              write_zoomlevel=for_write_zoom_level

              i = node.extent.start.line
              description = regexContextualComment(write_zoomlevel).match(enum_file[i-1-1][1])
              if description:
                 descText = description.group('condition')
                 descList = descText.split(';')
              else:
                 descList = ['','','']

              counter = 0
              for e in node.get_children():
                 counter+=1
              
                 if counter < 4:
                    text = ' '.join(t.spelling for t in e.get_tokens())

                 if counter == 1: # the intializers
                    if description:
                        if len(descList) >1:
                           if descList[0] != '':
                              text = descList[0]
                    if text != ' ':
                       write_zoomlevel=for_write_zoom_level
                       write_strings(write_zoomlevel)
                       inside_comment_flag[write_zoomlevel]=True
                       last_comment_str[write_zoomlevel] += text
                       lastcommentlinematched[write_zoomlevel] = e.extent.start.line                        

                 if counter == 2: # the condition
                    write_zoomlevel=for_write_zoom_level
                    write_strings(write_zoomlevel)
                    if description:
                        if len(descList) == 1:
                           text = descList[0]
                        if len(descList) > 1:
                           if descList[1].strip() == '':
                              text = 'true'
                           else:
                              text = descList[1]
                    
                    string_tmp[write_zoomlevel]+= '\n'+  indentation_level*tab + 'while ('+text+')''\n'
                    indentation_level+=1

                 #if counter == 3: keep the increment in text variable and put it at the end
                 if counter == 4: #process the body
                     breakContext='FOR_STMT'
                     new_last_line = process_node(e, new_last_line)
                     if len(descList) > 2:
                       if descList[2] != '':
                          text = descList[2]

              write_zoomlevel=for_write_zoom_level
              if text != ' ':
                  write_strings(write_zoomlevel)
                  inside_comment_flag[write_zoomlevel]=True
                  last_comment_str[write_zoomlevel] += text
                  lastcommentlinematched[write_zoomlevel] = e.extent.start.line     
                                  
              decrease_depthlevel()                   
              string_tmp[write_zoomlevel]+= (indentation_level-1)*tab +'endwhile'+'\n'+'\n'
              indentation_level-=1  

           return new_last_line #process_for_stmt

        #############################################################################################
        def process_continue_stmt(node, last_line):
           new_last_line = last_line
           return new_last_line #process_continue_stmt

        #############################################################################################
        def process_break_stmt(node, last_line):
           nonlocal breakContext
           nonlocal write_zoomlevel, string_tmp, indentation_level
           nonlocal caseLevel, caseNumber
           new_last_line = last_line
                   
           if breakContext == 'SWITCH_STMT':
              decrease_depthlevel() 
              #write last else in string                  
              string_tmp[write_zoomlevel]+= (indentation_level-1)*tab+'else(no)'+'\n'
              
           if breakContext == 'BIGSWITCH_STMT':
              decrease_depthlevel() 

           return new_last_line #process_break_stmt

        #############################################################################################
        def process_return_stmt(node, last_line,write_zoomlevel):
           nonlocal returnFound
           returnFound=True
           new_last_line = last_line
           write_strings(write_zoomlevel)
           string_tmp[write_zoomlevel]+= "\nstop\n"
           return new_last_line #process_return_stmt

        #############################################################################################
        #Recursive function to process a node
        def process_node(node, last_line):
           nonlocal diagram_zoomlevel, lastcommentlinematched, last_comment_str
           new_last_line = last_line
           #print_nodeK('Process node ',node)

           #handle annotations since last_line
           
           write_zoomlevel = 0 
           for i, line in enum_file:
              if i in range (last_line, node.extent.start.line):
                 for zoom_it2 in range(0,diagram_zoomlevel+1):
                   anyactionannotation = regexActionComment(zoom_it2).match(line)
                   if anyactionannotation:
                      write_zoomlevel=zoom_it2
                      break

                 #actions
                 if anyactionannotation:
                      #this line continues a previous multi-line action annotation
                      if lastcommentlinematched[write_zoomlevel] == i-1:
                         last_comment_str[write_zoomlevel]+='\\n'+anyactionannotation.group('action')
                      #first line of action annotation
                      else:
                          write_strings(write_zoomlevel)
                          inside_comment_flag[write_zoomlevel]=True
                          last_comment_str[write_zoomlevel] += anyactionannotation.group('action')

                      lastcommentlinematched[write_zoomlevel] = i 

           
           new_last_line = node.extent.start.line

           # process node according to its kind
           #####################################
           if node.kind.name == 'CALL_EXPR':
              new_last_line = process_call_expr_node(node, new_last_line)
           elif node.kind.name == 'CXX_DELETE_EXPR':
              new_last_line = process_del_expr_node(node, new_last_line)
           elif node.kind.name == 'DECL_REF_EXPR':
              new_last_line = process_decl_ref_expr(node, new_last_line)
           elif node.kind.name == 'COMPOUND_STMT':
              new_last_line = process_compound_stmt(node, new_last_line)
           elif node.kind.name == 'IF_STMT':
              new_last_line = process_if_stmt(node, new_last_line)
           elif node.kind.name == 'CASE_STMT':
              new_last_line = process_case_stmt(node, new_last_line)
           elif node.kind.name == 'DEFAULT_STMT':
              new_last_line = process_default_stmt(node, new_last_line)
           elif node.kind.name == 'SWITCH_STMT':
              new_last_line = process_switch_stmt(node, new_last_line)
           elif node.kind.name == 'WHILE_STMT':
              new_last_line = process_while_stmt(node, new_last_line)
           elif node.kind.name == 'DO_STMT':
              new_last_line = process_do_stmt(node, new_last_line)
           elif node.kind.name == 'FOR_STMT':
              new_last_line = process_for_stmt(node, new_last_line)
           elif node.kind.name == 'CONTINUE_STMT':
              new_last_line = process_continue_stmt(node, new_last_line)
           elif node.kind.name == 'BREAK_STMT':
              new_last_line = process_break_stmt(node, new_last_line)
           elif node.kind.name == 'RETURN_STMT':
              new_last_line = process_return_stmt(node, new_last_line,write_zoomlevel)
           elif node.kind.name == 'CXX_METHOD' or node.kind.name=='FUNCTION_DECL' or node.kind.name=='CONSTRUCTOR' or node.kind.name=='DESTRUCTOR':
              new_lst_line = process_method(node, new_last_line)
           else:
              for e in node.get_children():
                 new_last_line = process_node(e, new_last_line)
           return new_last_line #process_node      
             
        #############################################################################################
        string+='@startuml\n\nstart\n skinparam activityBackgroundColor #white \n'
             
        write_container=0
        if diagram_zoomlevel == 0:
          print('\n\n################### NEW FUNCTION ########################')
          print_tree(node)
        process_node(node,node.extent.start.line)
                                         
        write_strings(0)
        string+= '\n@enduml'
        #print (string)
        
        #write_htmlonline(string,outfile_str)
        write_txt(string,outfile_str)

      return  

   
#############################################################################################
#finds the functions to process. TO DO: It should be updated after build_db.py and method lookfor_lowestZoomactionAnnotation_inNode(nodeIN,zoom) have been included
def find_functions(node):

  global relevant_folder
  if node.kind.is_declaration():
    if node.kind.name=='CXX_METHOD' or node.kind.name=='FUNCTION_DECL' or node.kind.name=='CONSTRUCTOR' or node.kind.name=='DESTRUCTOR':
       if os.path.dirname(node.location.file.name) == relevant_folder:
         #is it in database?
         keyIN=node.get_usr()
         fileIN='flowdoc/aux_files/'+os.path.splitext(os.path.basename(node.location.file.name))[0]+'.flowdb'
         if read_single_flowdb(keyIN,fileIN):
           process_find_functions(node,read_single_flowdb.max_diagram_zoomlevel)
           return
  
  # Recurse for children of this node
  for c in node.get_children():
      #print ('children', c.kind)
      find_functions(c)

#############################################################################################
#### main program

index = clang.cindex.Index.create()
#tu = index.parse(sys.argv[1])
args=["-c","-x","c++","-Wall","-ansi"]
if len(sys.argv)>=2:
   args+=sys.argv[2:]   
#tu = index.parse("./src/t.cpp",args)
#tu_aux1=index.parse("./include/t.h",args, None, 2)
#tu_aux2=index.parse("./src/t.cpp",args)
tu = index.parse(sys.argv[1],args)
print ('Translation unit:', tu.spelling)
relevant_folder=os.path.dirname(tu.spelling)
for diagnostic in tu.diagnostics:
  print(diagnostic)
#global variable for the name of the input file. It will be defined later on.
infile_str=''
find_functions(tu.cursor)
#print(os.path.splitext(infile_str)[0])
#print(os.path.basename(infile_str))
#print(os.path.splitext(os.path.basename(infile_str))[0])

#f = open('flowdoc/'+os.path.splitext(os.path.basename(infile_str))[0]+".html","w")
#f.write(htmlonline_str)
#f.close()
