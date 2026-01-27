import { useState, useCallback } from 'react';

export const useMockStream = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '你好！我是 XSimple 智能助手。我可以帮你生成销售、用户增长或财务报表。请告诉我你的需求。' }
  ]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [reportData, setReportData] = useState(null);

  const generateResponse = useCallback(async (userQuery) => {
    setIsStreaming(true);
    
    // 添加用户消息
    const newUserMsg = { role: 'user', content: userQuery };
    setMessages(prev => [...prev, newUserMsg]);

    // 初始化AI空消息
    setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

    // 模拟AI思考逻辑
    let responseText = "";
    let mockData = null;

    if (userQuery.includes("销售")) {
      responseText = "好的，我正在为您生成**2023年度销售报表**。\n\n根据数据显示，第四季度的增长尤为明显，主要得益于双十一活动的推广。右侧将为您展示详细的趋势图表。";
      mockData = [
        { name: '1月', value: 4000 }, { name: '2月', value: 3000 },
        { name: '3月', value: 2000 }, { name: '4月', value: 2780 },
        { name: '5月', value: 1890 }, { name: '6月', value: 2390 },
      ];
    } else {
      responseText = "收到，但我是一个演示模型。如果您输入包含“**销售**”的指令，我将演示报表可视化的生成过程。";
    }

    // 模拟流式输出 (打字机效果)
    const chunks = responseText.split("");
    let currentText = "";

    for (let char of chunks) {
      await new Promise(resolve => setTimeout(resolve, 30)); // 模拟网络延迟
      currentText += char;
      
      setMessages(prev => {
        const newArr = [...prev];
        newArr[newArr.length - 1] = { role: 'assistant', content: currentText };
        return newArr;
      });
    }

    // 如果生成了报表数据，更新状态
    if (mockData) {
      setReportData({ title: "年度销售趋势分析", data: mockData });
    }

    setIsStreaming(false);
  }, []);

  return { messages, isStreaming, generateResponse, reportData };
};