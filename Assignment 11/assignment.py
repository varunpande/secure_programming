#!/usr/bin/python
####################################################################################
# Name: Varunkumar Pande
# Mav-Id: 1001722538
####################################################################################
import sys, re, sqlite3, os, stat, datetime

def error_func(error_msg=''):
    sys.stderr.write(str(error_msg)+"\n")
    sys.exit(1)

def logger(log_data):
    try:
        os.seteuid(0)
        file_handler = open(str(os.getcwd())+'/logger.txt','a')
        file_handler.write(str(datetime.datetime.now()) + " " + str(os.getuid()) + log_data + "\n")
    except Exception as msg:
        error_func(msg)
    finally:
        os.seteuid(os.getuid())
        file_handler.close()

class TelephoneListing:
    DB_CONNECT = None
    def __init__(self):
        try:
            # initialize the directory database
            if 'directory.db' in os.listdir(str(os.getcwd())):
                os.seteuid(0)
                TelephoneListing.DB_CONNECT = sqlite3.connect(str(os.getcwd())+'/directory.db')
                os.seteuid(os.getuid())
            else:
                os.seteuid(0)
                TelephoneListing.DB_CONNECT = sqlite3.connect(str(os.getcwd())+'/directory.db')
                TelephoneListing.DB_CONNECT.execute('''CREATE TABLE TELEPHONE_DIRECTORY
                (NAME           TEXT NOT NULL,
                PHONE          TEXT NOT NULL,
                PRIMARY KEY (NAME,PHONE));
                ''')
                os.chown(str(os.getcwd())+'/directory.db', 0, 0)
                os.chmod(str(os.getcwd())+'/directory.db',stat.S_IWRITE | stat.S_IREAD)
                # creating a log file
                fh_log = open(str(os.getcwd())+'/logger.txt','w')
                fh_log.close()
                os.chown(str(os.getcwd())+'/logger.txt', 0, 0)
                os.chmod(str(os.getcwd())+'/logger.txt',stat.S_IWRITE | stat.S_IREAD)
                os.seteuid(os.getuid())
        except Exception as msg:
            if 'directory.db' in os.listdir(str(os.getcwd())):
                os.remove(str(os.getcwd())+'/directory.db')
            if 'logger.txt' in os.listdir(str(os.getcwd())):
                os.remove(str(os.getcwd())+'/logger.txt')
            error_func(msg)
        finally:
            os.seteuid(os.getuid())

    def validate_person(self, person):
        person_pattern = re.compile(r"^[a-z][']?[a-z]+([,]?[ ][a-z][']?[a-z]+[-]?[ ]?[a-z]+[.]?)?$", re.IGNORECASE)
        match = person_pattern.search(person)
        # If match is found, person name is valid
        if match:
            return True   
        # If match is not found, person name is invalid
        else: 
            return False

    def validate_telephone(self, telephone):
        telephone_pattern  = re.compile(r"^(\d{5}[ .,])?(\d{5})$|^([+][1-9]\d{0,2}[. -]?|[1-9]\d{0,2}[. -]?|[+][1-9]\d{0,2}|\d{1,3})?(\d{2}[ ]\d{2}|[(][1-9]\d{1,2}[)][ ]?\d{3}|\d{3}[ -.]\d{3})?([., -]\d{2}[ ]\d{2}|[. -]\d{4})$|^([+][1-9]\d{0,2}[. -]?|[1-9]\d{0,2}[. -]?|[+][1-9]\d{0,2}|\d{1,3})?([ ]\d[ ][(][1-9]\d{1,2}[)][ ]?\d{3}|[ ]\d[ ]\d{3}[ -.]\d{3})?([., -]\d{2}[ ]\d{2}|[. -]\d{4})$|^(\d{4}[ .,])(\d{4})$")
        match = telephone_pattern.search(telephone)
        # If match is found, telephone number is valid
        if match:
            return True   
        # If match is not found, telephone number is invalid
        else: 
            return False

    def save_data(self, person, telephone):
        try:
            TelephoneListing.DB_CONNECT.execute('INSERT INTO TELEPHONE_DIRECTORY VALUES (?, ?);', (person, telephone))
            TelephoneListing.DB_CONNECT.commit()
            TelephoneListing.DB_CONNECT.close()
            logger(" ADD "+person)
        except sqlite3.IntegrityError:
            error_func("A similar record already exists!")
        except Exception as msg:
            error_func(msg)
        finally:
            TelephoneListing.DB_CONNECT.close()

    def del_telephone(self, telephone):
        try:
            db_cursor = TelephoneListing.DB_CONNECT.cursor()
            # fetch the record of the person to be deleted
            db_cursor.execute('SELECT NAME FROM TELEPHONE_DIRECTORY WHERE PHONE=(?);', (telephone,))
            person = db_cursor.fetchone()
            if person:
                TelephoneListing.DB_CONNECT.execute('DELETE FROM TELEPHONE_DIRECTORY WHERE PHONE=(?);', (telephone,))
                TelephoneListing.DB_CONNECT.commit()
                logger(" DEL "+person[0])
            else:
                sys.exit(1)
        except Exception as msg:
            error_func(msg)
        finally:
            TelephoneListing.DB_CONNECT.close()

    
    def del_person(self, person):
        try:
            db_cursor = TelephoneListing.DB_CONNECT.cursor()
            # fetch the record of the person to be deleted
            db_cursor.execute('SELECT NAME FROM TELEPHONE_DIRECTORY WHERE NAME=(?);', (person,))
            db_person = db_cursor.fetchone()
            if db_person:
                TelephoneListing.DB_CONNECT.execute('DELETE FROM TELEPHONE_DIRECTORY WHERE NAME=(?);', (person,))
                TelephoneListing.DB_CONNECT.commit()
                logger(" DEL "+person)
            else:
                sys.exit(1)
        except Exception as msg:
            error_func(msg)
        finally:
            TelephoneListing.DB_CONNECT.close()

    def list_data(self):
        try:
            db_cursor = TelephoneListing.DB_CONNECT.cursor()
            db_cursor.execute('SELECT * FROM TELEPHONE_DIRECTORY')
            display_data = db_cursor.fetchall()
            if len(display_data) > 0:
                print('person name \t telephone number')
                for p_name,p_number in display_data:
                    print(p_name + ' \t ' + p_number)
            else:
                print('Telephone Directory Empty!')
            logger(" LIST command executed")
        except Exception as msg:
            error_func(msg)
        finally:
            del db_cursor
            TelephoneListing.DB_CONNECT.close()

if __name__ == '__main__':
    os.seteuid(os.getuid())
    # check for number of arguments
    if len(sys.argv) == 1:
        print('Command Help!')
        print('\nPlease enter one of the following commands:\n')
        print("""ADD "<Person>" "<Telephone #>" - Add a new person to the database \nDEL "<Person>" - Remove someone from the database by name \nDEL "<Telephone #>" - Remove someone by telephone # \nLIST - Produce a list of the members of the database""")
        error_func()
    elif len(sys.argv)< 2 or len(sys.argv) > 4:
        error_func('Improper number of arguments')
    
    tl_obj = TelephoneListing()

    if sys.argv[1].upper() == 'ADD' and len(sys.argv) == 4:
        if tl_obj.validate_person(sys.argv[2]) and tl_obj.validate_telephone(sys.argv[3]):
            # save person and telephone
            tl_obj.save_data(sys.argv[2], sys.argv[3])
            sys.exit(0)
        else:
            error_func('Improper input')

    elif sys.argv[1].upper() == 'DEL' and len(sys.argv) == 3:
        if tl_obj.validate_person(sys.argv[2]):
            # del person data
            tl_obj.del_person(sys.argv[2])
            sys.exit(0)
        elif tl_obj.validate_telephone(sys.argv[2]):
            # del telephone data
            tl_obj.del_telephone(sys.argv[2])
            sys.exit(0)
        else:
            error_func('Improper input')
    
    elif sys.argv[1].upper() == 'LIST' and len(sys.argv) == 2:
        tl_obj.list_data()
        sys.exit(0)
    
    else:
        error_func('Improper number of arguments or wrong command entered!')