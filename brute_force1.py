import itertools
import string
import zipfile
import argparse

def extractFile(zFile, password):
    try:
        zFile.extractall(pwd=password)
        print "[+] Found password = " + password
        return True
    except:
        return False

def main():
    parser = argparse.ArgumentParser("%prog -f <zipfile>")
    parser.add_argument("-f", dest="zname", help="specify zip file")
    args = parser.parse_args()

    if (args.zname == None):
        print parser.usage
        exit(0)
    else:
        zname = args.zname

    zFile = zipfile.ZipFile(zname)
    #chars = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','0','1','2','3','4','5','6','7','8','9']
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits #+ string.punctuation
    attempts = 0
    for password_length in range(3, 4):
        for guess in itertools.product(chars, repeat=password_length):
            attempts += 1
            guess = ''.join(guess)
            #print('guess: '+ guess)
            found = extractFile(zFile, guess)
            if found == True:
                return 'password is {}. found in {} guesses.'.format(guess, attempts)
                exit(0)
            if guess[0]==guess[1] and guess[1] == guess[2]:
                print(guess, attempts)
    
    print('Password Not Found.')


if __name__ == "__main__":
    main()