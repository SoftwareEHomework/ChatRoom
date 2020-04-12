import tensorflow as tf
import json
model = tf.keras.models.load_model('./AI_write_novel.h5')
with open("./data/id2word.txt", 'r') as f:
    id_to_word = f.read().split()
with open("./data/word2id.json", 'r') as f:
    word_to_id = json.load(f)

def generate_text(model, start_string,num_generate = 1000):
  # 评估步骤（用学习过的模型生成文本）
  # 要生成的字符个数
    num_generate = 1000    #你可以调整这个参数
  # 将起始字符串转换为数字（向量化）
    input_eval = [word_to_id[s] for s in start_string]
    input_eval = tf.expand_dims(input_eval, 0)
  # 空字符串用于存储结果
    text_generated = []
  # 低温度会生成更可预测的文本
  # 较高温度会生成更令人惊讶的文本
  # 可以通过试验以找到最好的设定
    temperature = 0.4     #可调整
  # 这里批大小为 1
    model.reset_states()
    for i in range(num_generate):
        predictions = model(input_eval)
      # 删除批次的维度
        predictions = tf.squeeze(predictions, 0)
      # 用分类分布预测模型返回的字符
        predictions = predictions / temperature
        predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()

      # 把预测字符和前面的隐藏状态一起传递给模型作为下一个输入
        input_eval = tf.expand_dims([predicted_id], 0)

        text_generated.append(id_to_word[predicted_id])

    return (start_string + ''.join(text_generated))

print(generate_text(model, start_string="萧炎",num_generate=100))