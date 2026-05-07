# project-managment
Dog Breed Recognition Encyclopedia APP - User Manual
Document Information	Content
Software Name	Dog Breed Recognition Encyclopedia APP
Version Number	v1.0.0
Release Date	2026
Development Team	Zhang Yeheng, Wen Minxing, Luo Shirui, Zhang Chenjia, Li Zhuolin
Table of Contents
1.Software Introduction
2.System Requirements
3.Installation Guide
4.Quick Start
5.Detailed Function Description
6.Frequently Asked Questions
7.Technical Support
8.Appendix: Supported Dog Breed List (Partial)

1. Software Introduction
1.1 What is this software?
Dog Breed Recognition Encyclopedia APP is a deep learning-based desktop application that helps you quickly identify a dog's breed from its photo, and provides detailed encyclopedic knowledge and scientific feeding advice for the breed. All core recognition processes run locally on your device, with no photo uploads to external servers, fully protecting your data privacy.
1.2 Key Features
Feature	Description
Image Recognition	Upload a dog photo and get breed identification results within 3-5 seconds
Encyclopedia Query	Access complete information of 200+ dog breeds, including personality, weight, lifespan, feeding key points and more
Alias Recognition	Support identification of common colloquial names (e.g. Husky, Golden Retriever, Teddy, Corgi)
Baidu Encyclopedia Backup Query	Automatically connect to the internet to supplement information when there is no local match for the breed
Offline Operation	Core recognition function is fully available offline, no internet required for basic use
Scientific Dog Raising Guide	Built-in general and breed-specific scientific feeding guidelines for dog owners
1.3 Target Users
Families planning to raise a dog and need to choose a suitable breed
Curious people who encounter unknown dogs on the street and want to learn about them
Pet industry practitioners (veterinarians, pet groomers, pet shop staff)
Staff of animal rescue stations
Dog breed enthusiasts and canine knowledge learners

2. System Requirements
2.1 Minimum Requirements
Configuration Item	Requirement
Operating System	Windows 10/11 (64-bit)
Processor	Intel Core i5 or equivalent performance
RAM	8GB
Hard Disk Space	500MB available space
Network	Optional (required for Baidu Encyclopedia backup query)
2.2 Recommended Requirements
Configuration Item	Requirement
Operating System	Windows 11 (64-bit)
Processor	Intel Core i7 or higher
RAM	16GB
Hard Disk Space	1GB available space
Network	Broadband internet connection
2.3 Supported Image Formats
JPG/JPEG
PNG
BMP

3. Installation Guide
3.1 Software Acquisition
Method 1: Portable Version (Recommended)
Download DogBreedApp_v1.0.0.exe from the project release page
File size: approx. 500MB (includes pre-trained model files)
Method 2: Source Code Version (For Developers)
Clone the code repository from GitHub
Install Python dependencies manually
3.2 Installation Steps (Portable Version)
1.Download the exe file
oDownload DogBreedApp_v1.0.0.exe from the specified official release channel
2.Double-click to run
oNo installation required, directly double-click the exe file to launch the program
oThe first startup may take slightly longer (approx. 10-15 seconds) due to model loading
3.Security Prompt Handling
oIf Windows Defender pops up a warning, click "More info" → "Run anyway"
oThis software is fully open source, non-toxic and harmless, with no malicious code
3.3 Installation Steps (Source Code Version)
For developers and tech enthusiasts, you can run the program via source code with the following steps:
bash
运行
# 1. Clone the code repository
git clone https://github.com/your-repo/dog-breed-app.git

# 2. Enter the project directory
cd dog-breed-app

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the program
python main.py

4. Quick Start
4.1 Launch the Software
Double-click DogBreedApp_v1.0.0.exe and wait for approx. 5-10 seconds. You will see the main interface, including the photo selection button, recognition button, image preview area, and result display area.
4.2 3-Step Quick Recognition
Step 1: Select a Dog Photo
1.Click the 【Select Dog Photo】 button in the upper left corner
2.In the pop-up file dialog, locate the dog photo you want to identify
3.Select the photo and click "Open"
✅ The photo will be displayed in the left preview area after successful loading
Step 2: Start Breed Recognition
1.Confirm that the photo preview is correct and clear
2.Click the 【Identify Dog Breed】 button
3.Wait for 3-5 seconds, the interface will display "🔍 Recognizing..." during the process
Step 3: View Recognition Results
After the recognition is completed, the right area will display the complete results, including:
Dog Breed Name (bold and highlighted)
Detailed Information (alias, size, weight, height, lifespan, personality, coat, origin, feeding key points)
Breed Introduction (origin, history and characteristic stories of the breed)
Recognition Confidence Score (accuracy reference of the identification result)

5. Detailed Function Description
5.1 Image Selection & Preview
Function Point	Description
Supported Formats	JPG, PNG, BMP
Preview Size	500×400 pixels, maintaining the original aspect ratio
HD Photo Support	Support HD photos taken by mobile phones (automatic compression)
Error Handling	Clear prompts for damaged images or unsupported formats
Tips:
Choose clear front or side face photos for higher recognition accuracy
Avoid backlit, blurry photos, or photos with multiple dogs in the frame
5.2 Dog Breed Recognition
Recognition Speed: 3-5 seconds (varies depending on computer configuration)
Recognition Range: 200+ common dog breeds, covering 99% of common pet dogs
Recognition Accuracy: ≥80% for mainstream common breeds
Examples of Supported Dog Breeds:
Category	Breed Examples
Small Dogs	Corgi, Pomeranian, Chihuahua, Shih Tzu, Pug, Yorkshire Terrier
Medium Dogs	Golden Retriever, Labrador Retriever, Siberian Husky, Border Collie, German Shepherd
Large Dogs	Rottweiler, Doberman Pinscher, Alaskan Malamute, Great Dane
Terriers	Scottish Terrier, West Highland White Terrier
Poodles	Standard Poodle, Miniature Poodle, Toy Poodle (Teddy)
5.3 Encyclopedia Information Display
After successful recognition, you will see the following 11 information fields, plus the recognition confidence score:
Field	Description
Breed Name	Standard official Chinese and English name
Alias	Common colloquial names and nicknames
Size	Toy/Small/Medium/Large/Extra Large Dog
Weight	Weight range for male and female dogs
Height	Height range for male and female dogs
Lifespan	Average lifespan range
Personality	Typical character traits
Coat	Coat type, length and common colors
Origin	Country/region of breed origin
Feeding Key Points	Precautions for diet, exercise, health care and disease prevention
Detailed Introduction	Breed history, origin stories and core characteristics
5.4 Alias Mapping Function
The software supports common colloquial names for dogs, and automatically maps them to standard breed names. Examples are as follows:
Colloquial Name	Mapped Standard Breed
Husky	Siberian Husky
Golden Retriever	Golden Retriever
Corgi	Pembroke Welsh Corgi
Border Collie	Border Collie
Teddy	Toy Poodle
German Shepherd	German Shepherd Dog
Labrador/Lab	Labrador Retriever
5.5 Baidu Encyclopedia Backup Query
When the identified breed is not available in the local database, the software will automatically connect to the internet to query Baidu Encyclopedia for supplementary information:
Network Requirement: Internet connection required
Query Content: Get a brief introduction within 500 words from Baidu Encyclopedia
Source Identification: The result will be marked with "【Information Source】: Baidu Encyclopedia"
5.6 General Scientific Dog Raising Guide
The software has a built-in comprehensive scientific dog raising guide, covering core content such as diet management, health care, daily exercise, behavior training, living environment and emergency first aid knowledge, which is suitable for all dog owners to learn and reference.

6. Frequently Asked Questions (FAQs)
Q1: The software cannot be launched, and there is no response when double-clicking?
Possible Causes:
Missing VC++ runtime library
Blocked by anti-virus software
Solutions:
1.Run the program as administrator
2.Temporarily turn off the anti-virus software or add the software to the whitelist
3.Install the VC++ Runtime Library
Q2: The recognition result is inaccurate, and the breed is always identified incorrectly?
Possible Causes:
The picture is not clear enough
Poor shooting angle of the photo
The dog is a mixed-breed dog
Suggestions:
1.Choose a clear front or side face photo of the dog
2.Avoid backlit, blurry or overexposed photos
3.For mixed-breed dogs, the software will prompt "May be a mixed-breed or rare breed"
Q3: The recognition speed is very slow, exceeding 10 seconds?
Possible Causes:
Low computer configuration
Running multiple resource-intensive programs at the same time
Suggestions:
1.Close other programs that occupy memory and CPU resources
2.Ensure that the computer meets the minimum system requirements
3.Slow first startup is a normal phenomenon due to model loading
Q4: Baidu Encyclopedia query failed?
Possible Causes:
No internet connection
Baidu Encyclopedia interface changes
Solutions:
1.Check your internet connection status
2.Try again later
3.The software will display user-friendly prompts such as "Network connection timeout"
Q5: The software prompts "Image is too large"?
Description:
The software will automatically process large images, but may prompt an error if the image exceeds 50 million pixels.
Solution:
Compress the image with other software first, or select a photo with a smaller size.
Q6: How to update the software?
Portable Version:
Download the new version of the exe file and replace the old file directly
Source Code Version:
bash
运行
git pull
pip install -r requirements.txt
Q7: Will the software collect my photos?
Absolutely NOT! This software runs completely locally:
All recognition processes are completed on your computer
No photos will be uploaded to any external server
Baidu Encyclopedia query only sends the breed name, no image data is transmitted

7. Technical Support
7.1 Contact Information
If you encounter problems or have suggestions, you can contact us through the following methods:
Contact Method	Details
Project Homepage	https://github.com/your-repo/dog-breed-app
Issue Submission	GitHub Issues
Email	support@dogbreedapp.com (sample email)
7.2 Problem Feedback Template
When submitting a problem, please include the following information to help us locate and solve the problem quickly:
plaintext
【Problem Description】:
【Reproduction Steps】:
1. 
2. 
3. 

【Screenshot/Screen Recording】: (if any)

【System Information】:
- Windows Version: Win10 / Win11
- Software Version: v1.0.0
- RAM Size: XX GB

【Log Information】: (if any)
7.3 Update Log
Version	Release Date	Update Content
v1.0.0	2026	Initial version release
		• Support 200+ dog breed recognition
		• Complete encyclopedia information display
		• Alias mapping function
		• Baidu Encyclopedia backup query
		• Built-in scientific dog raising guide

9.Appendix: Supported Dog Breed List (Partial)
Breed Name	English Name	Size Category
Pembroke Welsh Corgi	Pembroke Welsh Corgi	Small Dog
Cardigan Welsh Corgi	Cardigan Welsh Corgi	Small Dog
Chihuahua	Chihuahua	Toy Dog
Pomeranian	Pomeranian	Small Dog
Shih Tzu	Shih Tzu	Small Dog
Pug	Pug	Small Dog
Yorkshire Terrier	Yorkshire Terrier	Small Dog
Golden Retriever	Golden Retriever	Medium Dog
Labrador Retriever	Labrador Retriever	Medium Dog
German Shepherd	German Shepherd Dog	Medium Dog
Siberian Husky	Siberian Husky	Medium Dog
Border Collie	Border Collie	Medium Dog
English Bulldog	Bulldog	Medium Dog
Boxer	Boxer	Medium Dog
Rottweiler	Rottweiler	Large Dog
Doberman Pinscher	Doberman Pinscher	Large Dog
Great Dane	Great Dane	Extra Large Dog
Saint Bernard	Saint Bernard	Extra Large Dog
Alaskan Malamute	Alaskan Malamute	Large Dog
Standard Poodle	Standard Poodle	Large Dog
Miniature Poodle	Miniature Poodle	Small Dog
Toy Poodle	Toy Poodle	Toy Dog
Thank you for using the Dog Breed Recognition Encyclopedia APP!
We hope this software can help you better understand dogs, raise dogs scientifically, and enjoy the wonderful time with your furry friends.
