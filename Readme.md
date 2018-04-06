# What is it
Encrypt your files before storing them on the cloud. Decrypt them when you want them back.

My main backup medium is an external hard drive and my main fear is that if the hard drive gets stolen, then I will lose all of my data.
I don't trust cloud services that claim to do encryption. In addition, tools like 'boxcryptor' require having all of your data in your pc, which I can't do, because my external hard drive is much bigger than my laptop's SSD.
Therefore, I wanted something that could encrypt my data in chunks, without having to have everything in one place, and that would allow me to add extra things later.

# Features
- Encrypts a folder and all of its subfolders
- Hides folder structure
- Hides file names
- Can sync with folder changes
- Can append files to folders even though other physical files have been deleted (e.g. when running out of space on your pc)

# Examples
Assume you have a folder called 'backup' that has the following structure:

```
backup/
├── files
│   ├── personal
│   │   ├── file1.txt
│   │   └── payments.txt
│   └── work
│       ├── John
│       │   ├── expenses.txt
│       │   └── holidays.txt
│       └── important_file.txt
└── photos
    ├── 2016
    │   └── UK
    │       ├── 510px-Flag_of_the_United_Kingdom.svg.png
    │       └── Flag_of_the_United_Kingdom.svg
    └── 2017
        ├── India
        │   ├── 510px-Flag_of_India.svg.png
        │   └── Flag_of_India.svg
        └── USA
            ├── 320px-Flag_of_the_United_States.svg.png
            └── Flag_of_the_United_States.svg
            
10 directories, 11 files
```

#### 1a. Example encryption (start here):
```sh
$ python cloud-crypto.py -e backup/
```
- Creates a folder named 'out_e/' containing the encrypted files. 
- (Secret) Creates a file named 'cloud-key.key'. This is password protected and contains the key used for encrypting/decrypting. This file must be kept secret!
- (Secret) Created a file named 'metadata.txt'. This file contains the necessary information to decrypt your files. This file must be kept secret!

#### 1b. Example decryption (start here):
```
$ python cloud-crypto.py -d out_e/ -m metadata.txt -k cloud-key.key
```
- Creates a folder named 'out_d' containing the same files and structure as the initial 'backup' folder.


#### 2a. Example encryption with additional files:

Assume that you add extra files in the folder. e.g. you add images for 2016/France. You don't want to re-encrypt everything. Only the new files.
```
python cloud-crypto.py -e backup/ -m metadata.txt -k cloud-key.key -v
Total files in folder: 13
file 'backup/files/personal/file1.txt' hasn't changed!
file 'backup/files/personal/payments.txt' hasn't changed!
file 'backup/files/work/important_file.txt' hasn't changed!
file 'backup/files/work/John/holidays.txt' hasn't changed!
file 'backup/files/work/John/expenses.txt' hasn't changed!
file 'backup/photos/2017/USA/Flag_of_the_United_States.svg' hasn't changed!
file 'backup/photos/2017/USA/320px-Flag_of_the_United_States.svg.png' hasn't changed!
file 'backup/photos/2017/India/510px-Flag_of_India.svg.png' hasn't changed!
file 'backup/photos/2017/India/Flag_of_India.svg' hasn't changed!
encrypted file 'backup/photos/2016/France/Flag_of_France.svg'                           <-----------
encrypted file 'backup/photos/2016/France/510px-Flag_of_France.svg.png'                 <-----------
file 'backup/photos/2016/UK/Flag_of_the_United_Kingdom.svg' hasn't changed!
file 'backup/photos/2016/UK/510px-Flag_of_the_United_Kingdom.svg.png' hasn't changed!
encrypted 3/13!
```
- '-v' flag enables more info. Notice that only 3 files were encrypted, as the others didn't change.


#### 2b. Example decryption with additional files:
This is always the same! (same as 1b.)
```
$ python cloud-crypto.py -d out_e/ -m metadata.txt -k cloud-key.key
```

#### 3. Example encryption with sync:
If you delete a file, then it will be deleted from the encrypted. e.g. deleting backup/files/personal/payments.txt
(Same command as 2a.)
```
$ python cloud-crypto.py -d out_e/ -m metadata.txt -k cloud-key.key -v
```

#### 4. Large files that cannot be stored for long
If your photos folder is too large to encrypt it all at once on your hard drive or you can't copy it in your machine due to space requirements, you can copy parts of it on your pc.

e.g. so far you have encrypted photos of 2016 and 2017. Now, you can delete folders '2016', '2017' and copy from your hard drive folder '2015'. Then you can append '2015' into the rest using the '-a' flag:
```
python cloud-crypto.py -e backup/ -m metadata.txt -k cloud-key.key -v -a
```

Now if you decrypt you will get the following structure (notice how 2015 has been appended):
```
out_d
└── backup
    ├── files
    │   ├── personal
    │   │   └── file1.txt
    │   └── work
    │       ├── John
    │       │   ├── expenses.txt
    │       │   └── holidays.txt
    │       └── important_file.txt
    └── photos
        ├── 2015
        │   └── Germany
        │       └── IMG_050.png
        ├── 2016
        │   ├── France
        │   │   ├── 510px-Flag_of_France.svg.png
        │   │   └── Flag_of_France.svg
        │   └── UK
        │       ├── 510px-Flag_of_the_United_Kingdom.svg.png
        │       └── Flag_of_the_United_Kingdom.svg
        └── 2017
            ├── India
            │   ├── 510px-Flag_of_India.svg.png
            │   └── Flag_of_India.svg
            └── USA
                ├── 320px-Flag_of_the_United_States.svg.png
                └── Flag_of_the_United_States.svg

14 directories, 13 files
```
