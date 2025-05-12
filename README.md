# G05_KeaProject
软件开发第五组Kea系统代码仓库

## Intro(概要介绍)
Kea is a general and practical testing tool based on the idea of property-based testing for finding functional (logic) bugs in mobile (GUI) apps. Kea currently supports Android and HarmonyOS.
This project has optimized and enhanced the large model guidance path traversal strategy (LLMPolicy) for Kea, with the main tasks including:
### LLM Strategy Optimization(LLM策略优化)
1. Improved the UI trap detection mechanism by adopting multi-modal similarity judgment.
2. Enhanced the completeness of status description by adding key component information.
3. Optimized the LLM prompt engineering by adding business scenario context.
4. Implemented a context saving and reuse mechanism for UI traps.
5. Diversity measurement
## Installation and Quickstart(使用说明)
**Prerequisites**  
Python 3.8+  
adb or hdc cmd tools available  
Connect an Android / HarmonyOS device or emulator to your PC (using Android Studio)
### User Manual (用户手册) (https://kea-docs.readthedocs.io/en/latest/part-theory/introduction.html)
### Installation
Enter the following commands to install kea.
```
git clone https://github.com/ecnusse/Kea.git
cd Kea
pip install -e .
```
### Quick Start
示例(具体参考用户手册):
```
kea -f example/example_property.py -a example/omninotes.apk
```
## Experimental Dataset
Android APP : Omni-notes, MyExpenses, Amaza File Manager, AntennaPod...
