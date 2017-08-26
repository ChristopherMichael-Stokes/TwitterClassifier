import tflearn
import unicodedata
import re
import _pickle
import numpy as np

class ProcessInput:

  def __init__(self):
    with open('../tweet_gathering/tweets.pkl','rb') as f:
      self.list_of_text=_pickle.load(f)


  def enumerateLabels(self,label):
    label=label.lower()
    return{
      "london":0,
      "birmingham":1,
      "manchester":2,
      "glasgow":3,
      "newcastle":4,
      "sheffield":5,
      "los_angeles":6,
      "new_york":7
    }.get(label,-1)

  def cleanText(self,text):
    text=re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ",text)
    text=re.sub(r"\'s", " \'s", text)
    text=re.sub(r"\'ve", " \'ve",text)
    text=re.sub(r"n\'t", " n\'t",text)
    text=re.sub(r"\'re", " \'re",text)
    text=re.sub(r"\'d", " \'d",text)
    text=re.sub(r"\'ll", " \'ll",text)
    text=re.sub(r",", " , ", text)
    text=re.sub(r"!", " ! ",text)
    text=re.sub(r"\(", " \( ",text)
    text=re.sub(r"\)", " \) ",text)
    text=re.sub(r"\?", " \? ",text)
    text=re.sub(r"\s{2,}", " ",text)
    return text.strip().lower()

  def textToVec(self,text,vp):
    new_text = np.array(list(vp.fit_transform(text)))
    vp.save("vocab.txt")
    return new_text

  def writeBack(self):    

    text_tmp=[line.split("¦")[1] for line in self.list_of_text]
    labels_tmp=[line.split("¦")[0] for line in self.list_of_text]

    print("\t***** making vocabulary *****")
    #print(type(text_tmp))

    text_tmp = [line.strip() for line in text_tmp]
    text_tmp = [self.cleanText(line) for line in text_tmp]
    vp = tflearn.data_utils.VocabularyProcessor(max_document_length=72,min_frequency=0)
    text = self.textToVec(text_tmp,vp)

    #print(text[0])
    print("\t***** enumerating labels *****")

    labels = [self.enumerateLabels(label) for label in labels_tmp]
    labels = np.asarray(labels, dtype=np.int_)
    labels = tflearn.data_utils.to_categorical(labels,nb_classes=8)

    #print(labels[0])
    #print(labels[len(labels)-1])
    
    with open('processedInput.pkl', 'wb') as f:  
      labels_and_text = [labels,text]    
      _pickle.dump(labels_and_text,f)
  
  def singleInput(self,text_string):
    #make text a single element list 
    vp = tflearn.data_utils.VocabularyProcessor(max_document_length=72,min_frequency=0)
    vp = vp.restore('vocab.txt')
    text = self.textToVec([self.cleanText(text_string)],vp)
    vp.save("vocab.txt")
    return text

def main():
  pI = ProcessInput()
  pI.writeBack()

if __name__=="__main__":
  main()