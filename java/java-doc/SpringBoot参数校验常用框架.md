# SpringBoot参数校验常用框架

一般的参数校验框架有两个选择

1. Hibernate-validator 注解 针对Controller的接受参数进行校验
2. Assert 断言 针对业务逻辑进行校验

# 使用Hibernate-validator进行注解式参数校验

## 依赖选择

在SpringBoot早期版本之前自动会引入validator，较新版本需要我们自己去引入

对于SpringBoot集成Hibernate-validator我们可以使用`spring-boot-starter-validation`，也可以是直接引入`hibernate-validator`。

```xml
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
            <version>3.1.2</version>
        </dependency>
```

```xml
    <dependency>
      <groupId>org.hibernate.validator</groupId>
      <artifactId>hibernate-validator</artifactId>
      <version>8.0.1.Final</version>
      <scope>compile</scope>
    </dependency>
```

## 简单使用

Java API规范(JSR303)定义了Bean校验的标准validation-api，但没有提供实现。hibernate validation是对这个规范的实现，并增加了校验注解如@Email、@Length等。

Spring Validation是对hibernate validation的二次封装，用于支持spring mvc参数自动校验。

在简单使用上主要是使用其注解进行参数校验，主要注解如下：

@NotEmpty 被注释的字符串的不能为 null 也不能为空
@NotBlank 被注释的字符串非 null，并且必须包含一个非空白字符
@Null 被注释的元素必须为 null
@NotNull 被注释的元素必须不为 null
@AssertTrue 被注释的元素必须为 true
@AssertFalse 被注释的元素必须为 false
@Pattern(regex=,flag=)被注释的元素必须符合指定的正则表达式
@Email 被注释的元素必须是 Email 格式。
@Min(value)被注释的元素必须是一个数字，其值必须大于等于指定的最小值
@Max(value)被注释的元素必须是一个数字，其值必须小于等于指定的最大值
@DecimalMin(value)被注释的元素必须是一个数字，其值必须大于等于指定的最小值
@DecimalMax(value) 被注释的元素必须是一个数字，其值必须小于等于指定的最大值
@Size(max=, min=)被注释的元素的大小必须在指定的范围内
@Digits(integer, fraction)被注释的元素必须是一个数字，其值必须在可接受的范围内
@Past被注释的元素必须是一个过去的日期
@Future 被注释的元素必须是一个将来的日期

使用时在方法参数中进行验证**一定一定不要忘记在类上加上 `@Validated` 注解了**，这个参数可以告诉 SpringBoot 去校验方法参数。或者在方法参数前直接使用 `@Validated` 注解而不是`@Valid`注解。

![](https://prod.huayu.asia:9000/picgo/2023/08/08/20230808171559.png)

## 全局异常处理

如果校验出现问题，一般会抛出两种异常：

MethodArgumentNotValidException或者ConstraintViolationException异常，但是注意他这两种异常抛出会导致请求400，并且返回结果也不是我们rest风格的返回，需要我们进行一次全局异常处理来实现我们想要的效果。

```java
@RestControllerAdvice
public class CommonExceptionHandler {

    @ExceptionHandler({MethodArgumentNotValidException.class})
    @ResponseStatus(HttpStatus.OK)
    @ResponseBody
    public Result handleMethodArgumentNotValidException(MethodArgumentNotValidException ex) {
        BindingResult bindingResult = ex.getBindingResult();
        StringBuilder sb = new StringBuilder("校验失败:");
        for (FieldError fieldError : bindingResult.getFieldErrors()) {
            sb.append(fieldError.getField()).append("：").append(fieldError.getDefaultMessage()).append(", ");
        }
        String msg = sb.toString();
       return Result.fail(BusinessCode.参数校验失败, msg);
    }

    @ExceptionHandler({ConstraintViolationException.class})
    @ResponseStatus(HttpStatus.OK)
    @ResponseBody
    public Result handleConstraintViolationException(ConstraintViolationException ex) {
        return Result.fail(BusinessCode.参数校验失败, ex.getMessage());
    }
}
```

## 进阶使用

### 分组校验

在实际项目中，可能多个方法需要使用同一个DTO类来接收参数，而不同方法的校验规则很可能是不一样的。这个时候，简单地在DTO类的字段上加约束注解无法解决这个问题。因此，spring-validation支持了分组校验的功能，专门用来解决这类问题。

还是上面的例子，比如保存User的时候，UserId是可空的，但是更新User的时候，UserId的值必须>=10000000000000000L；其它字段的校验规则在两种情况下一样。这个时候使用分组校验的代码示例如下：

约束注解上声明适用的分组信息groups

```java
@Data
public class UserDTO {

    @Min(value = 10000000000000000L, groups = Update.class)
    private Long userId;

    @NotNull(groups = {Save.class, Update.class})
    @Length(min = 2, max = 10, groups = {Save.class, Update.class})
    private String userName;

    @NotNull(groups = {Save.class, Update.class})
    @Length(min = 6, max = 20, groups = {Save.class, Update.class})
    private String account;

    @NotNull(groups = {Save.class, Update.class})
    @Length(min = 6, max = 20, groups = {Save.class, Update.class})
    private String password;

    /**
     * 保存的时候校验分组
     */
    public interface Save {
    }

    /**
     * 更新的时候校验分组
     */
    public interface Update {
    }
}
```

@Validated注解上指定校验分组

```java
@PostMapping("/save")
public Result saveUser(@RequestBody @Validated(UserDTO.Save.class) UserDTO userDTO) {
    // 校验通过，才会执行业务逻辑处理
    return Result.ok();
}

@PostMapping("/update")
public Result updateUser(@RequestBody @Validated(UserDTO.Update.class) UserDTO userDTO) {
    // 校验通过，才会执行业务逻辑处理
    return Result.ok();
}
```

### 嵌套校验

前面的示例中，DTO类里面的字段都是基本数据类型和String类型。但是实际场景中，有可能某个字段也是一个对象，这种情况先，可以使用嵌套校验。

比如，上面保存User信息的时候同时还带有Job信息。需要注意的是，此时DTO类的对应字段必须标记@Valid注解。

```java
@Data
public class UserDTO {

    @Min(value = 10000000000000000L, groups = Update.class)
    private Long userId;

    @NotNull(groups = {Save.class, Update.class})
    @Length(min = 2, max = 10, groups = {Save.class, Update.class})
    private String userName;

    @NotNull(groups = {Save.class, Update.class})
    @Length(min = 6, max = 20, groups = {Save.class, Update.class})
    private String account;

    @NotNull(groups = {Save.class, Update.class})
    @Length(min = 6, max = 20, groups = {Save.class, Update.class})
    private String password;

    @NotNull(groups = {Save.class, Update.class})
    @Valid
    private Job job;

    @Data
    public static class Job {

        @Min(value = 1, groups = Update.class)
        private Long jobId;

        @NotNull(groups = {Save.class, Update.class})
        @Length(min = 2, max = 10, groups = {Save.class, Update.class})
        private String jobName;

        @NotNull(groups = {Save.class, Update.class})
        @Length(min = 2, max = 10, groups = {Save.class, Update.class})
        private String position;
    }

    /**
     * 保存的时候校验分组
     */
    public interface Save {
    }

    /**
     * 更新的时候校验分组
     */
    public interface Update {
    }
}
```

嵌套校验可以结合分组校验一起使用。还有就是**嵌套集合校验会对集合里面的每一项都进行校验**，例如`List<Job>`字段会对这个list里面的每一个Job对象都进行校验。

### 集合校验

如果请求体直接传递了json数组给后台，并希望对数组中的每一项都进行参数校验，即直接传递过来就是一个list不是我们自己的对象。此时，如果我们直接使用java.util.Collection下的list或者set来接收数据，参数校验并不会生效！我们可以使用自定义list集合来接收参数：

包装List类型，并声明@Valid注解

```java
public class ValidationList<E> implements List<E> {

    @Delegate // @Delegate是lombok注解  该注解将 List上的所有方法转发到我们的list属性上  类似实现了一个包装器
    @Valid // 一定要加@Valid注解
    public List<E> list = new ArrayList<>();

    // 一定要记得重写toString方法
    @Override
    public String toString() {
        return list.toString();
    }
}
```

如果校验不通过，会抛出NotReadablePropertyException，同样可以使用统一异常进行处理。

比如，我们需要一次性保存多个User对象，Controller层的方法可以这么写：

```java
@PostMapping("/saveList")
public Result saveList(@RequestBody @Validated(UserDTO.Save.class) ValidationList<UserDTO> userList) {
    // 校验通过，才会执行业务逻辑处理
    return Result.ok();
}
```

### 自定义校验

业务需求总是比框架提供的这些简单校验要复杂的多，我们可以自定义校验来满足我们的需求。

主要分为两步：

#### 自定义约束注解

```java
package asia.huayu.anno;


import asia.huayu.validator.PhoneValidator;
import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.Documented;
import java.lang.annotation.Retention;
import java.lang.annotation.Target;

import static java.lang.annotation.ElementType.*;
import static java.lang.annotation.RetentionPolicy.RUNTIME;

/**
 * @Description:
 * @Author: ZiYu
 * @Created on: 2023/08/08 17:35
 * @Since:
 */
@Target({METHOD, FIELD, ANNOTATION_TYPE, CONSTRUCTOR, PARAMETER})
@Retention(RUNTIME)
@Documented
@Constraint(validatedBy = {PhoneValidator.class})
public @interface Phone {

    // 默认错误消息
    String message() default "手机号错误";

    // 分组
    Class<?>[] groups() default {};

    // 负载
    Class<? extends Payload>[] payload() default {};

    @Target({METHOD, FIELD, ANNOTATION_TYPE, CONSTRUCTOR, PARAMETER})
    @Retention(RUNTIME)
    @Documented
    @interface List {
        Phone[] value();
    }
}
```

#### 编写自定义约束校验器

实现ConstraintValidator接口

```java
package asia.huayu.validator;


import asia.huayu.anno.Phone;
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * @Description:
 * @Author: ZiYu
 * @Created on: 2023/08/08 17:36
 * @Since:
 */
public class PhoneValidator implements ConstraintValidator<Phone, String> {
    // 构建正则表达式，用于实现之后的字符串校验
    private static final Pattern PATTERN = Pattern.compile("^((13[0-9])|(15[^4])|(18[0,2,3,5-9])|(17[0-8])|(147))\\d{8}");

    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        // 不为null才进行校验
        if (value != null || value.length() != 0) {
            // 使用正则表达式校验
            Matcher matcher = PATTERN.matcher(value);
            return matcher.find();
        }
        return true;
    }
}

```

我们可以直接在对应属性上使用该注解。

### 编程式校验

上面的示例都是基于注解来实现自动校验的，在某些情况下，我们可能希望以编程方式调用验证。这个时候可以注入javax.validation.Validator对象，然后再调用其api。

```java
@Autowired
private javax.validation.Validator globalValidator;

// 编程式校验
@PostMapping("/saveWithCodingValidate")
public Result saveWithCodingValidate(@RequestBody UserDTO userDTO) {
    Set<ConstraintViolation<UserDTO>> validate = globalValidator.validate(userDTO, UserDTO.Save.class);
    // 如果校验通过，validate为空；否则，validate包含未校验通过项
    if (validate.isEmpty()) {
        // 校验通过，才会执行业务逻辑处理

    } else {
        for (ConstraintViolation<UserDTO> userDTOConstraintViolation : validate) {
            // 校验失败，做其它逻辑
            System.out.println(userDTOConstraintViolation);
        }
    }
    return Result.ok();
}
```

### 快速失败(Fail Fast)

Spring Validation默认会校验完所有字段，然后才抛出异常。可以通过一些简单的配置，开启Fali Fast模式，一旦校验失败就立即返回。

```java
@Bean
public Validator validator() {
    ValidatorFactory validatorFactory = Validation.byProvider(HibernateValidator.class)
            .configure()
            // 快速失败模式
            .failFast(true)
            .buildValidatorFactory();
    return validatorFactory.getValidator();
}
```

## 实现原理

### 方法中引用数据类型校验

对于引用数据类型，我们将注解标注在类的属性上，而在我们请求到的时候`RequestResponseBodyMethodProcessor.java`会负责解析所有request参数，也就是在这时进行参数校验。

校验方法如下：

```java
	/**
	 * Throws MethodArgumentNotValidException if validation fails.
	 * @throws HttpMessageNotReadableException if {@link RequestBody#required()}
	 * is {@code true} and there is no body content or if there is no suitable
	 * converter to read the content with.
	 */
	@Override
	public Object resolveArgument(MethodParameter parameter, @Nullable ModelAndViewContainer mavContainer,
			NativeWebRequest webRequest, @Nullable WebDataBinderFactory binderFactory) throws Exception {

		parameter = parameter.nestedIfOptional();
		Object arg = readWithMessageConverters(webRequest, parameter, parameter.getNestedGenericParameterType());
		String name = Conventions.getVariableNameForParameter(parameter);

		if (binderFactory != null) {
			WebDataBinder binder = binderFactory.createBinder(webRequest, arg, name);
			if (arg != null) {
                // 进行参数校验
				validateIfApplicable(binder, parameter);
				if (binder.getBindingResult().hasErrors() && isBindExceptionRequired(binder, parameter)) {
					throw new MethodArgumentNotValidException(parameter, binder.getBindingResult());
				}
			}
			if (mavContainer != null) {
				mavContainer.addAttribute(BindingResult.MODEL_KEY_PREFIX + name, binder.getBindingResult());
			}
		}

		return adaptArgumentIfNecessary(arg, parameter);
	}
```

`validateIfApplicable`方法如下

```java
	/**
	 * Validate the binding target if applicable.
	 * <p>The default implementation checks for {@code @javax.validation.Valid},
	 * Spring's {@link org.springframework.validation.annotation.Validated},
	 * and custom annotations whose name starts with "Valid".
	 * @param binder the DataBinder to be used
	 * @param parameter the method parameter descriptor
	 * @since 4.1.5
	 * @see #isBindExceptionRequired
	 */
	protected void validateIfApplicable(WebDataBinder binder, MethodParameter parameter) {
		Annotation[] annotations = parameter.getParameterAnnotations();
		for (Annotation ann : annotations) {
			Object[] validationHints = ValidationAnnotationUtils.determineValidationHints(ann);
			if (validationHints != null) {
				binder.validate(validationHints);
				break;
			}
		}
	}
```

而获取`validationHints`的方法`ValidationAnnotationUtils.determineValidationHints`如下

```java
	/**
	 * Determine any validation hints by the given annotation.
	 * <p>This implementation checks for {@code @javax.validation.Valid},
	 * Spring's {@link org.springframework.validation.annotation.Validated},
	 * and custom annotations whose name starts with "Valid".
	 * @param ann the annotation (potentially a validation annotation)
	 * @return the validation hints to apply (possibly an empty array),
	 * or {@code null} if this annotation does not trigger any validation
	 */
	@Nullable
	public static Object[] determineValidationHints(Annotation ann) {
		Class<? extends Annotation> annotationType = ann.annotationType();
		String annotationName = annotationType.getName();
		if ("javax.validation.Valid".equals(annotationName)) {
			return EMPTY_OBJECT_ARRAY;
		}
		Validated validatedAnn = AnnotationUtils.getAnnotation(ann, Validated.class);
		if (validatedAnn != null) {
			Object hints = validatedAnn.value();
			return convertValidationHints(hints);
		}
		if (annotationType.getSimpleName().startsWith("Valid")) {
			Object hints = AnnotationUtils.getValue(ann);
			return convertValidationHints(hints);
		}
		return null;
	}
```

也就是获取其方法上的注解，并根据注解转换为对应的ValidationHints，之后进行对应的validate。

注意这里`javax.validation.Valid`注解返回的是空对象数组，所以Valid注解目前应该不直接参与参数校验，而是以Valid开头的注解获取其内部的ValidationHints。

### 方法级别的参数校验实现原理

上面提到的将参数一个个平铺到方法参数中，然后在每个参数前面声明约束注解的校验方式，就是方法级别的参数校验。

实际上，这种方式可用于任何Spring Bean的方法上，比如Controller/Service等。其底层实现原理就是AOP，具体来说是通过MethodValidationPostProcessor动态注册AOP切面，然后使用MethodValidationInterceptor对切点方法织入增强。

```java
public class MethodValidationPostProcessor extends AbstractBeanFactoryAwareAdvisingPostProcessorimplements InitializingBean {
    @Override
    public void afterPropertiesSet() {
        //为所有`@Validated`标注的Bean创建切面
        Pointcut pointcut = new AnnotationMatchingPointcut(this.validatedAnnotationType, true);
        //创建Advisor进行增强
        this.advisor = new DefaultPointcutAdvisor(pointcut, createMethodValidationAdvice(this.validator));
    }

    //创建Advice，本质就是一个方法拦截器
    protected Advice createMethodValidationAdvice(@Nullable Validator validator) {
        return (validator != null ? new MethodValidationInterceptor(validator) : new MethodValidationInterceptor());
    }
}
```

**不论以上两种校验方式实际上最终还是调用的`hibernate-validator`内的`isValid`方法**。

# 使用Assert 进行参数校验

Assert意为断言，即它断定某一个实际的运行值和预期想一样，否则就抛出异常。

Spring 对方法入参的检测借用了这个概念，其提供的 Assert 类拥有众多按规则对方法入参进行断言的方法，可以满足大部分方法入参检测的要求。

常用的判断方法如下这些：

![](https://prod.huayu.asia:9000/picgo/2023/08/09/20230809095715.png)

Spring提供的Assert 类通常会抛出`IllegalArgumentException`以及`IllegalStateException` 异常。

我们需要对这两种异常进行全局捕获。

但是其实我们可以自己封装一个Assert 类，模仿Spring的判断方法，抛出我们自定义的异常。

也可以直接使用Hutools的断言工具类,但它的弊端也是无法抛出自定义异常。