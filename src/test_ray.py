from sklearn.datasets import fetch_20newsgroups
from transformers import pipeline
import time
from datetime import timedelta
import psutil
import ray

# from https://towardsdatascience.com/parallel-inference-of-huggingface-transformers-on-cpus-4487c28abe23

test_data = fetch_20newsgroups(subset='test', shuffle=False, categories=['rec.motorcycles', 'rec.sport.baseball'], remove=('headers', 'footers', 'quotes'))

test_data = [text for text in test_data.data if text!='']
print('Number of text articles:', len(test_data))

pipe = pipeline(task = 'zero-shot-classification', model='typeform/distilbert-base-uncased-mnli', batch_size=1, device=-1)

prediction = pipe(test_data[100], ['motorcycle', 'baseball'])
print('Text:', prediction['sequence'])
print('Labels:', prediction['labels'])
print('Scores:', prediction['scores'])

start = time.time()

predictions = [pipe(text, ['motorcycle', 'baseball']) for text in test_data]

end = time.time()
print('Prediction time:', str(timedelta(seconds=end-start)))

num_cpus = psutil.cpu_count(logical=True)
print('Number of available CPUs:', num_cpus)

ray.init(num_cpus=num_cpus, ignore_reinit_error=True)

pipe_id = ray.put(pipe)

@ray.remote
def predict(pipeline, text_data, label_names):
    return pipeline(text_data, label_names)

start = time.time()
predictions = ray.get([predict.remote(pipe_id, text, ['motorcycle', 'baseball']) for text in test_data])
end = time.time()
print('Prediction time:', str(timedelta(seconds=end-start)))

ray.shutdown()
