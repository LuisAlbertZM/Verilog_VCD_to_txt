###################################################################################################
###################################################################################################
###################################################################################################
## Place    : MEXCO, Zapopan Jal.
## Date     : March 2015
## Description: This script reads a VCD dump variable file and creates
##              a new fie with all the information of a single signal
###################################################################################################
###################################################################################################
###################################################################################################

  ## IMPORTS SECTION ## 
import re
import sys
import os

############################################################
#CLASSES  
############################################################

#######################################
# Signal class
# This class is in charge of contain a variable and its data
class Signal:
    # Initialization method
    def __init__(self, var, sym):
        self.var    = var
        self.sym    = sym
        self.dat    = []
        if len(sym) > 1:    # The signal is split into multiple bits
            self.multibit   = True
        else:
            self.multibit   = False
   
    # Deleing object 
    def __del__(self):
        print 'Deleting objetct'

    # Method that is in charge of acquiring the data correspondent to the signal
    def acquire(self,IOFiles):
        # Opening and reading matching chars        
        print 'Extracting signal '+str(self.var)
        print 'Associated symbols: ' +str(self.sym) 
        vcdfile = IOFiles['vcd_file']   
        fs = IOFiles['output_directory'] + '/' + self.var + '.dat'
        #f = open(vcdfile)                   # Opening file     
        print '     ' + fs
        try:
            fil = open(fs,'w')
        except Exception:
            print 'ERROR: Error while creating %s file'%(fs)
            sys.exit
        #for x in i.dat:
        #    fil.write(str(x)+'\n')  
        word = ['']                         # Initializing string
        #fs = IOFiles['output_directory'] + '/' + self.var + '.dat'
        #open(fs)
        first = 1;                          # Flag Initialization indicating this is that's the 1st element
        # This checks if a multiple-bit word has multiple associated symbols
        if self.multibit == True:
            #for line in f:                  # On each lime looking for each of the symbols 
            with open(vcdfile,'r') as FILE:
                for line in FILE:    
                    for sym in self.sym: 
                        if re.match(r'^[x01]\s*'+re.escape(sym)+r'\s*\n',line): 
                            if first == 1:
                                if line[0] == 'x':
                                    word.append('0')
                                else:
                                    word.append(line[0])
                                if len(word) == len(self.sym):
                                    first = 0
                            else:
                                if line[0] == 'x':
                                    word[self.sym.index(sym)] = '0' 
                                else:
                                    word[self.sym.index(sym)] = line[0] 
                    # In the VCD file # means a new cycle and only the bits that change are written 
                    if re.match(r'^#',line) and first == 0:
                        fil.write(str(int(''.join(word),2))+'\n')
                fil.write(str(int(''.join(word),2))+'\n')
                # For multi-bit non-split signals and single-bi signals
        else:
            #print 'I\'m in single symbol signals'+str(self.sym[0])
            with open(vcdfile,'r') as FILE:
                for line in FILE:       
                    # Multi-bit non-split signals      
                    if re.match(r'^b[0-9]+'+re.escape(str(self.sym[0]))+r'\s*\n',line):
                        fil.write(str(int(line[1:len(line)-3],2))+'\n')
                    # Single-bit signals
                    elif re.match(r'^[0-9]'+re.escape(str(self.sym[0]))+r'\n',line): 
                        fil.write(str(int(''.join(line[0:len(line)-2],2),2))+'\n')
                    elif re.match(r'[x]',line):
                       fil.write('0\n') 
                       #print 'WARNING: Signal undefined in line: \'%s\', value set to 0'%(line)
        #f.close()  # Closing file
        fil.close() 

#######################################
# tools class
# This class handles the dunctions regarding read arguments from command line, 
#   as well as directory verification and creation  
class  tools():
    ##################################                             
    # Methods 
    ###################################
    # Description: This method returns all the variables and its associate
    # allsymbols preent on a VCD file
    def get_vars(self,fil):
        # variables declaration
        variables           = []
        AllSimvarDict       = {}
        try:
            vcd = open(fil,'r')               # Opening the file$
        except Exception:
            print 'ERROR: The specified VCD file does not exists' 
            sys.exit() 
        ## Getting all the different variables and allsymbols
        for line in vcd:                            # Scanning each line 
            matchLine = re.match(r'\$var',line)     # Matching current line  
            if matchLine:                           # If there's a match 
                try:                        # This try/except is intended to avoid repeated variables 
                    variables.index(line.split()[4])    
                except Exception:
                    variables.append(line.split()[4])   # Getting variables
                # Creating Dictionary with variables and associated symbols 
                # Variables
                AllSimvarDict.setdefault(line.split()[4], [])
                # Symbols
                AllSimvarDict[line.split()[4]].append(line.split()[3]) #It might fail
        vcd.close()
        return AllSimvarDict
        
    # This method will be in charge of cathching the data from the command line and 
    # Generate a group of commands that will be used on the main program
    def catchIn(self):
        #Initial values
        output      = {}
        vcdfile     = ''
        outdir      = ''
        odir        = '/home/luis/VCDFiles/'    # Defining default output default input directory 
        
        #Getting parameters from console
        for elem  in sys.argv:
            if elem == '-v'or elem == '--vcd':
                try:
                    output['vcd_file'] =  sys.argv[sys.argv.index(elem)+1]
                    print "VCD file: "+output['vcd_file']
                except Exception:
                    print "ERROR: No VCD file specified"
                    sys.exit()
            elif elem == '-o' or elem =='--output' :
                try:
                    output['output_directory'] = sys.argv[sys.argv.index(elem)+1]
                    print "Output directory: "+output['output_directory']
                except Exception:
                    print "ERROR: No output directory  specified"
        # Verifying data
        try:
            output['vcd_file']
        except Exception:
            print 'ERROR: No VCD file  specified'
            sys.exit()
        try:
            output['output_directory']
        except Exception:
            output['output_directory'] = odir
            print 'WARNING: No output directory specified, set to default: '+odir
        # Returning data
        return output

    # This method creates the output directory for the acquired data             
    def createOutputDirectory(self,directory):
        if not os.path.exists(directory):
            print 'INFO: Specified directory does not exists, creating output directory ...'
            try:
                os.system('mkdir %s'%(directory))
            except Exception:
                print 'ERROR: Unable to create the specified directory' 
        else:
            print 'WARNING: Selected directory already exists, overwriting data ...' 
    
############################################################
############################################################
## MAIN PROGRAM 
## Description: This program finds and clasifies all the 
##       variables coming from a VCD dump file
#############################################################
############################################################

## BODY OF THE PROGRAM ##


## variables declaration
varDict     = {}    # Empty dictionary which creates 
signals     = []    # Empty signals array
IOFiles     = {}

## *** MAIN program *** ##
# Creating array of signals objects 
t = tools() # This methids  handles the auciliary fuctions

IOFiles = t.catchIn()
varDict = t.get_vars(IOFiles['vcd_file'])
t.createOutputDirectory(IOFiles['output_directory'])

print "Created files:"
for i in varDict:
    x = Signal(i, varDict[i])
    x.acquire(IOFiles)
    del x
