# TweetRecommend

TweetRecommend is a project about social networks and machine learning. It is using machine learning get a classifications of the tweets of your personal account in different categories. 

I did use Django as BackendFramework for the developing, it is just a personal project, then I didn't implement a  good multiuser method, where you could select different accounts or create your own categories. You can do that by the administate site of Django.

This project use Scikit-Learn to implement the machine learning algorithms. All method as authentication and learning are implemented in the  python module MethodUtils.py. 

This project use Support Vector Machine, to get the learning in the "machine", beyond It use text-mining tecniques to get a better acuracy and perfomance. You can measure the accuracy and perfomance of the different models going to "Ver Métricas", or "Ver Métricas en una Cateroria", then the platform will create an image with the different algorithm metrics.

The project have been built as my career's tesis, then I didn't run the project in a own server, it has been only runned in the test server using python manage.py runserver "port"

I have created a file called requirements.txt where I have written the differents libraries of my enviroment, I have used Anaconda2 for the building of the project, but it was by an issue with scipy, if you don't have it, you can use pip install -r requirements.txt to install all libraries.

Finally, you will can see the tweets classified by the platform in the different categories, such as technology or politics without lose your time reading some tweets of the some different topics.

Thanks!
