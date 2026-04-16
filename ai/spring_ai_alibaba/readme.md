Spring AI 是 Spring 生态中用于集成人工智能能力的框架，简化了与大语言模型（LLM）、向量数据库等 AI 组件的集成。以下是其核心使用方式和示例：


### **一、核心功能**
1. **大语言模型（LLM）集成**：支持 OpenAI、Azure OpenAI、Anthropic、Google Gemini 等。
2. **提示词工程**：模板化提示词，支持动态参数注入。
3. **向量存储**：集成 Pinecone、Milvus、Redis 等向量数据库，用于检索增强生成（RAG）。
4. **工具调用**：让 LLM 调用外部工具（如计算器、API）。


### **二、快速入门（以 OpenAI 为例）**

#### **1. 环境准备**
- JDK 17+
- Maven/Gradle
- OpenAI API Key（需注册并获取）


#### **2. 依赖配置（Maven）**
```xml
<dependencies>
    <!-- Spring AI OpenAI 集成 -->
    <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
        <version>0.8.1</version> <!-- 最新版本请参考官方文档 -->
    </dependency>
    <!-- Spring Boot 基础 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter</artifactId>
    </dependency>
</dependencies>
```


#### **3. 配置文件（application.properties）**
```properties
# OpenAI API 配置
spring.ai.openai.api-key=你的OpenAI_API_Key
spring.ai.openai.base-url=https://api.openai.com/v1
# 可选：默认模型
spring.ai.openai.chat.options.model=gpt-3.5-turbo
```


#### **4. 基础示例：调用 LLM 生成文本**
```java
import org.springframework.ai.chat.ChatResponse;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.openai.OpenAiChatClient;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class SpringAiDemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(SpringAiDemoApplication.class, args);
    }

    // 注入 OpenAI 客户端（自动配置）
    @Bean
    CommandLineRunner run(OpenAiChatClient chatClient) {
        return args -> {
            // 1. 构建提示词
            String message = "用一句话介绍 Spring AI";
            Prompt prompt = new Prompt(message);

            // 2. 调用 LLM
            ChatResponse response = chatClient.call(prompt);

            // 3. 输出结果
            System.out.println("回答：" + response.getResult().getOutput().getContent());
        };
    }
}
```


### **三、进阶示例：提示词模板 + 动态参数**
使用模板引擎定义可复用的提示词，动态注入参数。

#### **1. 定义提示词模板（resources/prompts/weather-prompt.st）**
```
请预测{{city}}在{{date}}的天气，用简洁的语言回答。
```

#### **2. 代码中使用模板**
```java
import org.springframework.ai.chat.prompt.PromptTemplate;
import org.springframework.ai.chat.prompt.SystemPromptTemplate;
import org.springframework.ai.openai.OpenAiChatClient;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

import java.util.Map;

@Component
public class WeatherPredictor {

    private final OpenAiChatClient chatClient;

    // 注入客户端
    public WeatherPredictor(OpenAiChatClient chatClient) {
        this.chatClient = chatClient;
    }

    public String predict(String city, String date) {
        // 加载模板
        PromptTemplate promptTemplate = new PromptTemplate(
                new ClassPathResource("prompts/weather-prompt.st"),
                Map.of("city", city, "date", date)
        );

        // 生成提示词并调用
        return chatClient.call(promptTemplate.create()).getResult().getOutput().getContent();
    }
}
```


### **四、检索增强生成（RAG）示例**
结合向量数据库实现基于知识库的问答。

#### **1. 添加向量存储依赖（以 Pinecone 为例）**
```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-pinecone-spring-boot-starter</artifactId>
    <version>0.8.1</version>
</dependency>
```

#### **2. 配置 Pinecone**
```properties
spring.ai.pinecone.api-key=你的Pinecone_API_Key
spring.ai.pinecone.environment=你的环境（如us-east1-gcp）
spring.ai.pinecone.index-name=你的索引名
```

#### **3. 代码实现 RAG**
```java
import org.springframework.ai.document.Document;
import org.springframework.ai.embedding.EmbeddingClient;
import org.springframework.ai.openai.OpenAiChatClient;
import org.springframework.ai.retrieval.RetrievalClient;
import org.springframework.ai.retrieval.VectorStoreRetrievalClient;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class RagService {

    private final OpenAiChatClient chatClient;
    private final RetrievalClient retrievalClient;

    public RagService(OpenAiChatClient chatClient, VectorStore vectorStore, EmbeddingClient embeddingClient) {
        this.chatClient = chatClient;
        // 初始化检索客户端
        this.retrievalClient = new VectorStoreRetrievalClient(vectorStore, embeddingClient);
    }

    // 向向量库添加文档
    public void addDocuments(List<String> texts) {
        List<Document> documents = texts.stream()
                .map(text -> new Document(text))
                .toList();
        retrievalClient.add(documents);
    }

    // 基于知识库问答
    public String answer(String question) {
        // 1. 检索相关文档
        List<Document> relevantDocs = retrievalClient.retrieve(question);

        // 2. 构建包含上下文的提示词
        String context = relevantDocs.stream()
                .map(Document::getContent)
                .reduce((a, b) -> a + "\n" + b)
                .orElse("无相关信息");

        String promptText = String.format("基于以下上下文回答问题：\n%s\n问题：%s", context, question);

        // 3. 调用 LLM
        return chatClient.call(new Prompt(promptText)).getResult().getOutput().getContent();
    }
}
```


### **五、工具调用示例**
让 LLM 根据问题自动调用外部工具（如计算器）。

#### **1. 定义工具**
```java
import org.springframework.ai.tools.CalculatorTool;
import org.springframework.ai.tools.Tool;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class ToolConfig {

    // 注册计算器工具
    @Bean
    public List<Tool> tools() {
        return List.of(new CalculatorTool());
    }
}
```

#### **2. 使用工具调用客户端**
```java
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.openai.OpenAiChatClient;
import org.springframework.ai.tools.ToolCallingChatClient;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ToolService {

    private final ToolCallingChatClient toolClient;

    // 注入工具调用客户端（自动包装 LLM 客户端和工具）
    public ToolService(OpenAiChatClient chatClient, List<Tool> tools) {
        this.toolClient = new ToolCallingChatClient(chatClient, tools);
    }

    public String solveMathProblem(String question) {
        return toolClient.call(new Prompt(question)).getResult().getOutput().getContent();
    }
}
```


### **六、关键依赖说明**
- `spring-ai-openai-spring-boot-starter`：OpenAI 集成
- `spring-ai-anthropic-spring-boot-starter`：Anthropic（Claude）集成
- `spring-ai-pinecone-spring-boot-starter`：Pinecone 向量库
- `spring-ai-redis-spring-boot-starter`：Redis 向量库（适用于轻量场景）


### **七、注意事项**
1. 版本兼容性：Spring AI 仍在快速迭代，建议使用最新稳定版。
2. API Key 安全：避免硬编码，可使用环境变量或配置中心。
3. 成本控制：LLM 和向量库调用可能产生费用，需合理控制请求频率。

更多示例和文档可参考 [Spring AI 官方文档](https://spring.io/projects/spring-ai)。