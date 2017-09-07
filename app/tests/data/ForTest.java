package com.marin.qa.dummy;

/**
 * Created by ssun on 9/7/17.
 */
public class ForTest {

    @Test
    @FileParameters(value = "test.json", mapper = TestDefinitionMapper.class)
    public void test1(){

    }

    @Test
    @Parameters(method = "callMethod")
    public void test2(){

    }

    @Test
    @Parameters("test.json")
    public void test3(){}

    @Test
    @Parameters({"test.json, " +
            "test2.json, " +
            "test3.json"})
    public void test4(){}

    //@Test
    @FileParameters(value = "test.json", mapper = TestDefinitionMapper.class)
    public void test5(){}

    @Ignore
    @Test
    @FileParameters(value = "test.json", mapper = TestDefinitionMapper.class)
    public void test6(){}

    @Test
    @Parameters({"test1.json",
            "test.json, " +
            "test2.json, " +
            "test3.json",
             "test4.json"})
    public void test7(){}
}
