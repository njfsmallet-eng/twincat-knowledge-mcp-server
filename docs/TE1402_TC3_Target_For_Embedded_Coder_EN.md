---
title: "TE1402_TC3_Target_For_Embedded_Coder_EN"
product: "TE1402"
category: "Engineering_Tools"
tags: ["CODER", "EMBEDDED", "FOR", "TARGET"]
language: "EN"
document_type: "Manual"
version: "1.0.0"
source_pdf: "https://download.beckhoff.com/download/Document/automation/twincat3/TE1402_TC3_Target_For_Embedded_Coder_EN.pdf"
release_date: "2024-12-04"
---
Manual | EN TE1402 Twin CAT 3 | Target for Embedded Coder® 2024-12-04 | Version: 1.0.0

## Page 3

Table of contents Table of contents 1 Foreword.................................................................................................................................................... 5 1.1 Notes on the documentation............................................................................................................. 5 1.2 For your safety.................................................................................................................................. 6 1.3 Notes on information security............................................................................................................ 7 1.4 Documentation issue status.............................................................................................................. 8 2 Overview.................................................................................................................................................... 9 3 Installation............................................................................................................................................... 10 4 Licenses................................................................................................................................................... 11 5 Parameterization in Simulink®.............................................................................................................. 12 6 Restrictions............................................................................................................................................. 14 7 Support and Service............................................................................................................................... 17 TE1402 Version: 1.0.0 3

## Page 4

Table of contents 4 Version: 1.0.0 TE1402

## Page 5

Foreword 1 Foreword 1.1 Notes on the documentation This description is intended exclusively for trained specialists in control and automation technology who are familiar with the applicable national standards. For installation and commissioning of the components, it is absolutely necessary to observe the documentation and the following notes and explanations. The qualified personnel is obliged to always use the currently valid documentation. The responsible staff must ensure that the application or use of the products described satisfies all requirements for safety, including all the relevant laws, regulations, guidelines, and standards. Disclaimer The documentation has been prepared with care. The products described are, however, constantly under development. We reserve the right to revise and change the documentation at any time and without notice. No claims to modify products that have already been supplied may be made on the basis of the data, diagrams, and descriptions in this documentation. Trademarks Beckhoff®, Twin CAT®, Twin CAT/BSD®, TC/BSD®, Ether CAT®, Ether CAT G®, Ether CAT G10®, Ether CAT P®, Safety over Ether CAT®, Twin SAFE®, XFC®, XTS® and XPlanar® are registered and licensed trademarks of Beckhoff Automation Gmb H. If third parties make use of designations or trademarks used in this publication for their own purposes, this could infringe upon the rights of the owners of the said designations. Patents The Ether CAT Technology is covered, including but not limited to the following patent applications and patents: EP1590927, EP1789857, EP1456722, EP2137893, DE102015105702 and similar applications and registrations in several other countries. Ether CAT® is registered trademark and patented technology, licensed by Beckhoff Automation Gmb H, Germany Copyright © Beckhoff Automation Gmb H & Co. KG, Germany. The distribution and reproduction of this document as well as the use and communication of its contents without express authorization are prohibited. Offenders will be held liable for the payment of damages. All rights reserved in the event that a patent, utility model, or design are registered. TE1402 Version: 1.0.0 5

## Page 6

Foreword 1.2 For your safety Safety regulations Read the following explanations for your safety. Always observe and follow product-specific safety instructions, which you may find at the appropriate places in this document. Exclusion of liability All the components are supplied in particular hardware and software configurations which are appropriate for the application. Modifications to hardware or software configurations other than those described in the documentation are not permitted, and nullify the liability of Beckhoff Automation Gmb H & Co. KG. Personnel qualification This description is only intended for trained specialists in control, automation, and drive technology who are familiar with the applicable national standards. Signal words The signal words used in the documentation are classified below. In order to prevent injury and damage to persons and property, read and follow the safety and warning notices. Personal injury warnings DANGER Hazard with high risk of death or serious injury. WARNING Hazard with medium risk of death or serious injury. CAUTION There is a low-risk hazard that could result in medium or minor injury. Warning of damage to property or environment NOTICE The environment, equipment, or data may be damaged. Information on handling the product This information includes, for example: recommendations for action, assistance or further information on the product. 6 Version: 1.0.0 TE1402

## Page 7

Foreword 1.3 Notes on information security The products of Beckhoff Automation Gmb H & Co. KG (Beckhoff), insofar as they can be accessed online, are equipped with security functions that support the secure operation of plants, systems, machines and networks. Despite the security functions, the creation, implementation and constant updating of a holistic security concept for the operation are necessary to protect the respective plant, system, machine and networks against cyber threats. The products sold by Beckhoff are only part of the overall security concept. The customer is responsible for preventing unauthorized access by third parties to its equipment, systems, machines and networks. The latter should be connected to the corporate network or the Internet only if appropriate protective measures have been set up. In addition, the recommendations from Beckhoff regarding appropriate protective measures should be observed. Further information regarding information security and industrial security can be found in our https://www.beckhoff.com/secguide. Beckhoff products and solutions undergo continuous further development. This also applies to security functions. In light of this continuous further development, Beckhoff expressly recommends that the products are kept up to date at all times and that updates are installed for the products once they have been made available. Using outdated or unsupported product versions can increase the risk of cyber threats. To stay informed about information security for Beckhoff products, subscribe to the RSS feed at https:// www.beckhoff.com/secinfo. TE1402 Version: 1.0.0 7

## Page 8

Foreword 1.4 Documentation issue status Version Modifications 1.0.0 First release 8 Version: 1.0.0 TE1402

## Page 9

Overview 2 Overview Twin CAT 3 TE1402 Target for Embedded Coder® is an extension of the Twin CAT 3 TE1400 Target for Simulink®. All features of the Twin CAT Target for Simulink® can be used. In this documentation (Twin CAT 3 Target for Embedded Coder®) you will find restrictions and extensions of the Twin CAT Target for Simulink®. More Information Documentation Twin CAT 3 TE1400 Target for Simulink® TE1402 Version: 1.0.0 9

## Page 10

Installation 3 Installation The same installation and setup requirements apply as described in Twin CAT 3 Target for Simulink® for version 2.x.xxx. Deviating and other installation requirements • MATLAB® R2022b or higher • Math Works® Embedded Coder TM Installation for Twin CAT 3.1 Build 4026 Name in the UI: TE1402 | Twin CAT 3 Target for Embedded Coder® Command line: tcpkg install TE1402. Target For Embedded Coder. XAE Installation for Twin CAT 3.1 Build 4024 The installation for Twin CAT 3.1 Build 4024 is part of the setup Twin CAT 3 Tools for MATLAB® and Simulink® and is installed automatically. 10 Version: 1.0.0 TE1402

## Page 11

Licenses 4 Licenses In addition to the TE1400 Twin CAT 3 Target for Simulink® license, you need the TE1402 Twin CAT 3 Target for Embedded Coder® license on your engineering PC. With regard to Twin CAT runtimes, the same licenses are required as for the Twin CAT 3 Target for Simulink®. This means that you do not need any additional runtime licenses if you already use Twin CAT objects in your runtime that were compiled with the Twin CAT 3 Target for Simulink® or Twin CAT 3 Target for MATLAB®. TE1402 Version: 1.0.0 11

## Page 12

Parameterization in Simulink® 5 Parameterization in Simulink® Using Embedded Coder® together with Twin CAT Set the system target file to Twin Cat Ert.tlc. Command Line Interface (CLI): Twin CAT. Module Generator. Simulink. Model Export Config. Show Model Param(model Name,'Sys tem Target File','Twin Cat Ert.tlc'); Or in the User Interface (UI) via the Configuration Parameters in the Simulink® model at Code Generation > System target file. Sample in MATLAB®: SIMD instruction set extensions In the „Simulink® Instruction Set Extensions“ sample, you will learn how to create a Simulink® model with the Twin CAT 3 Target for Embedded Coder, which uses SIMD instruction set extensions to accelerate model execution time. 12 Version: 1.0.0 TE1402

## Page 13

Parameterization in Simulink® Twin CAT. Module Generator. Samples. Start('Simulink Instruction Set Extensions') CPU of the target system must support instruction sets Make sure that the target system on which you want to execute the generated object supports the set instruction set extension. When the object is loaded, the Twin CAT runtime checks the availability of the instruction sets and compares them with the instruction sets used in the object. If the CPU does not meet the requirements, the object is not loaded and a corresponding error message is issued in Twin CAT XAE. The model can be built after parameterization via Apps > Embedded Coder > Generate Code. TE1402 Version: 1.0.0 13

## Page 14

Restrictions 6 Restrictions DSP System Toolbox™ AVX2 code replacement library The DSP System Toolbox™ AVX2 code replacement library requires the Twin CAT. XAE. Public SDK >4.9.0 and is therefore limited to Twin CAT 3.1. Build 4026. https://de.mathworks.com/help/dsp/ug/use-intel-avx2-code-replacement-library-to-generate-simd-code- from-simulink-blocks.html SIMD for Arm®64 platforms Neon instruction sets are only supported on MATLAB® R2024a. For R2014a, you must install the „Embedded Coder Support Package for Arm® Cortex®-A Processors“ package via the MATLAB® Add-on Explorer (for Beckhoff Embedded PCs CX82xx and CX9240). From MATLAB® R2024b, it is no longer necessary to install the package separately. Quick reference guide 1. Set the Device vendor and Device type to Arm® Compatible and Arm® Cortex®-A (64-bit) to generate the code specific for Beckhoff Embedded PCs CX82xx and CX9240. 2. Select „Neon v7“ as hardware instruction set extensions and activate „Optimize reductions“. 14 Version: 1.0.0 TE1402

## Page 15

Restrictions 3. Only select Twin CAT OS (Arm®V8-A) as the build platform. TE1402 Version: 1.0.0 15

## Page 16

Restrictions ð You can use this configuration to compile the Simulink® model. Ne10 Code Replacement Library Currently not yet supported. Generate Alloc Fcn If Reusable code and Generate Alloc Fcn=off are recognized, the Single Instance Limitation is activated. Generate Alloc Fcn is set to off by default. 16 Version: 1.0.0 TE1402

## Page 17

Support and Service 7 Support and Service Beckhoff and their partners around the world offer comprehensive support and service, making available fast and competent assistance with all questions related to Beckhoff products and system solutions. Download finder Our download finder contains all the files that we offer you for downloading. You will find application reports, technical documentation, technical drawings, configuration files and much more. The downloads are available in various formats. Beckhoff's branch offices and representatives Please contact your Beckhoff branch office or representative for local support and service on Beckhoff products! The addresses of Beckhoff's branch offices and representatives round the world can be found on our internet page: www.beckhoff.com You will also find further documentation for Beckhoff components there. Beckhoff Support Support offers you comprehensive technical assistance, helping you not only with the application of individual Beckhoff products, but also with other, wide-ranging services: • support • design, programming and commissioning of complex automation systems • and extensive training program for Beckhoff system components Hotline: +49 5246 963-157 e-mail: support@beckhoff.com Beckhoff Service The Beckhoff Service Center supports you in all matters of after-sales service: • on-site service • repair service • spare parts service • hotline service Hotline: +49 5246 963-460 e-mail: service@beckhoff.com Beckhoff Headquarters Beckhoff Automation Gmb H & Co. KG Huelshorstweg 20 33415 Verl Germany Phone: +49 5246 963-0 e-mail: info@beckhoff.com web: www.beckhoff.com TE1402 Version: 1.0.0 17

## Page 19

More Information: www.beckhoff.com/te1402 Beckhoff Automation Gmb H & Co. KG Hülshorstweg 20 33415 Verl Germany Phone: +49 5246 9630 info@beckhoff.com www.beckhoff.com
