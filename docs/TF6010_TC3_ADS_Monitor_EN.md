---
title: "TF6010 Twin CAT 3"
product: "TF6010"
category: "Communication"
tags: ["ADS", "CAT", "TWIN"]
language: "EN"
document_type: "Manual"
version: "1.0"
source_pdf: "https://download.beckhoff.com/download/Document/automation/twincat3/TF6010_TC3_ADS_Monitor_EN.pdf"
release_date: "2021-01-27"
---
Manual | EN TF6010 Twin CAT 3 | ADS Monitor 2021-01-27 | Version: 1.0
## Page 3

Table of contents Table of contents 1 Foreword.................................................................................................................................................... 5 1.1 Notes on the documentation.............................................................................................................. 5 1.2 Safety instructions............................................................................................................................. 6 2 Overview..................................................................................................................................................... 7 3 Installation................................................................................................................................................ 11 3.1 Installation....................................................................................................................................... 11 3.2 Licensing......................................................................................................................................... 14 TF6010 Version: 1.0 3
## Page 4

Table of contents 4 Version: 1.0 TF6010
## Page 5

Foreword 1 Foreword 1.1 Notes on the documentation This description is only intended for the use of trained specialists in control and automation engineering who are familiar with applicable national standards. It is essential that the documentation and the following notes and explanations are followed when installing and commissioning the components. It is the duty of the technical personnel to use the documentation published at the respective time of each installation and commissioning. The responsible staff must ensure that the application or use of the products described satisfy all the requirements for safety, including all the relevant laws, regulations, guidelines and standards. Disclaimer The documentation has been prepared with care. The products described are, however, constantly under development. We reserve the right to revise and change the documentation at any time and without prior announcement. No claims for the modification of products that have already been supplied may be made on the basis of the data, diagrams and descriptions in this documentation. Trademarks Beckhoff®, Twin CAT®, Ether CAT®, Ether CAT G®, Ether CAT G10®, Ether CAT P®, Safety over Ether CAT®, Twin SAFE®, XFC®, XTS® and XPlanar® are registered trademarks of and licensed by Beckhoff Automation Gmb H. Other designations used in this publication may be trademarks whose use by third parties for their own purposes could violate the rights of the owners. Patent Pending The Ether CAT Technology is covered, including but not limited to the following patent applications and patents: EP1590927, EP1789857, EP1456722, EP2137893, DE102015105702 with corresponding applications or registrations in various other countries. Ether CAT® is a registered trademark and patented technology, licensed by Beckhoff Automation Gmb H, Germany Copyright © Beckhoff Automation Gmb H & Co. KG, Germany. The reproduction, distribution and utilization of this document as well as the communication of its contents to others without express authorization are prohibited. Offenders will be held liable for the payment of damages. All rights reserved in the event of the grant of a patent, utility model or design. TF6010 Version: 1.0 5
## Page 6

Foreword 1.2 Safety instructions Safety regulations Please note the following safety instructions and explanations! Product-specific safety instructions can be found on following pages or in the areas mounting, wiring, commissioning etc. Exclusion of liability All the components are supplied in particular hardware and software configurations appropriate for the application. Modifications to hardware or software configurations other than those described in the documentation are not permitted, and nullify the liability of Beckhoff Automation Gmb H & Co. KG. Personnel qualification This description is only intended for trained specialists in control, automation and drive engineering who are familiar with the applicable national standards. Description of symbols In this documentation the following symbols are used with an accompanying safety instruction or note. The safety instructions must be read carefully and followed without fail! DANGER Serious risk of injury! Failure to follow the safety instructions associated with this symbol directly endangers the life and health of persons. WARNING Risk of injury! Failure to follow the safety instructions associated with this symbol endangers the life and health of per- sons. CAUTION Personal injuries! Failure to follow the safety instructions associated with this symbol can lead to injuries to persons. NOTE Damage to the environment or devices Failure to follow the instructions associated with this symbol can lead to damage to the environment or equipment. Tip or pointer This symbol indicates information that contributes to better understanding. 6 Version: 1.0 TF6010
## Page 7

Overview 2 Overview The TF6010 TC3 ADS Monitor records the ADS communication from the Twin CAT Message Router. This concerns as well the communication of ADS devices among each other, if they are on the local or on a remote system. The Twin CAT ADS Monitor can be downloaded from the Beckhoff FTP Server. The ADS Monitor integrates into the TC3 XAE development in the Visual Studio Menue of Twin CAT. The toolbar enables to start/stop recording of the ADS communication. By the selection of a recorded message the tool window will be splitted to display the ADS/AMS in clear text and in hex format. The ADS Monitor connects to the local system when the tool window is opened. It is possible to connect to a remote target, if the ADS Monitor is installed and the Tc Ams Log.exe is started on the remote target. TF6010 Version: 1.0 7
## Page 8

Overview Path to AMS/ADS Logger (Tc Amslog.exe) Windows C:\Twin CAT\Functions\TF6010-ADS-Monitor\Logger Windows CE /Hard Disk/System The ADS monitor provides to way to filter the messages: Capture Filter: Allows to filter during recording for AMS information (e.g. Net Id, Port) Display Filter: Allows to filter after recording for AMS and ADS information (e.g. Index-Group/Offset, Data) 8 Version: 1.0 TF6010
## Page 9

Overview The ADS monitor provides the possibility to send ADS commands to test ADS devices (e.g. PLC, NC) or custom ADS Servers. The ADS commands can be ordered in a command group and run cyclically. All base ADS commands can be configured and executed separately. TF6010 Version: 1.0 9
## Page 10

Overview 10 Version: 1.0 TF6010
## Page 11

Installation 3 Installation 3.1 Installation The following section describes how to install the Twin CAT 3 Function for Windows-based operating systems. ü The Twin CAT 3 Function setup file was downloaded from the Beckhoff website. 1. Run the setup file as administrator. To do this, select the command Run as administrator in the context menu of the file. ð The installation dialog opens. 2. Accept the end user licensing agreement and click Next. TF6010 Version: 1.0 11
## Page 12

Installation 3. Enter your user data. 4. If you want to install the full version of the Twin CAT 3 Function, select Complete as installation type. If you want to install the Twin CAT 3 Function components separately, select Custom. 12 Version: 1.0 TF6010
## Page 13

Installation 5. Select Next, then Install to start the installation. ð A dialog box informs you that the Twin CAT system must be stopped to proceed with the installation. 6. Confirm the dialog with Yes. TF6010 Version: 1.0 13
## Page 14

Installation 7. Select Finish to exit the setup. ð The Twin CAT 3 Function has been successfully installed and can be licensed (see Licensing [} 14]). 3.2 Licensing The Twin CAT 3 function can be activated as a full version or as a 7-day test version. Both license types can be activated via the Twin CAT 3 development environment (XAE). Licensing the full version of a Twin CAT 3 Function A description of the procedure to license a full version can be found in the Beckhoff Information System in the documentation "Twin CAT 3 Licensing". Licensing the 7-day test version of a Twin CAT 3 Function A 7-day test version cannot be enabled for a Twin CAT 3 license dongle. 1. Start the Twin CAT 3 development environment (XAE). 2. Open an existing Twin CAT 3 project or create a new project. 3. If you want to activate the license for a remote device, set the desired target system. To do this, select the target system from the Choose Target System drop-down list in the toolbar. ð The licensing settings always refer to the selected target system. When the project is activated on the target system, the corresponding Twin CAT 3 licenses are automatically copied to this system. 14 Version: 1.0 TF6010
## Page 15

Installation 4. In the Solution Explorer, double-click License in the SYSTEM subtree. ð The Twin CAT 3 license manager opens. 5. Open the Manage Licenses tab. In the Add License column, check the check box for the license you want to add to your project (e.g. "TF6420: TC3 Database Server"). 6. Open the Order Information (Runtime) tab. ð In the tabular overview of licenses, the previously selected license is displayed with the status “missing”. TF6010 Version: 1.0 15
## Page 16

Installation 7. Click 7-Day Trial License... to activate the 7-day trial license. ð A dialog box opens, prompting you to enter the security code displayed in the dialog. 8. Enter the code exactly as it is displayed and confirm the entry. 9. Confirm the subsequent dialog, which indicates the successful activation. ð In the tabular overview of licenses, the license status now indicates the expiry date of the license. 10. Restart the Twin CAT system. ð The 7-day trial version is enabled. 16 Version: 1.0 TF6010
## Page 18

More Information: www.beckhoff.com/tf6010 Beckhoff Automation Gmb H & Co. KG Hülshorstweg 20 33415 Verl Germany Phone: +49 5246 9630 info@beckhoff.com www.beckhoff.com
