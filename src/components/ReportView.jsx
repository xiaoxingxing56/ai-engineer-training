import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { FileBarChart, TrendingUp, Calendar, Target } from 'lucide-react';

const ReportView = ({ data }) => {
  if (!data) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-gray-400 bg-white rounded-l-2xl">
        <div className="w-16 h-16 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full flex items-center justify-center mb-6 opacity-70 shadow-sm">
          <FileBarChart size={32} className="text-indigo-500" />
        </div>
        <h3 className="text-lg font-semibold text-gray-700 mb-2">报表预览</h3>
        <p className="text-gray-500 text-sm max-w-xs text-center">在此处预览生成的 AI 报表，包含详细的数据图表和关键洞察</p>
      </div>
    );
  }

  return (
    <div className="h-full p-6 bg-white rounded-l-2xl overflow-y-auto">
      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 p-8 rounded-2xl shadow-sm border border-indigo-100">
        <div className="flex items-center mb-6">
          <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center mr-4 shadow-md">
            <TrendingUp size={24} className="text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-1">{data.title}</h2>
            <div className="flex items-center text-sm text-gray-600">
              <Calendar size={14} className="mr-2" />
              <span>由 XSimple AI 助手自动生成</span>
            </div>
          </div>
        </div>
        
        <div className="h-[400px] w-full bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data.data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#6b7280' }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#6b7280' }} />
              <Tooltip 
                contentStyle={{ 
                  borderRadius: '10px', 
                  border: 'none', 
                  boxShadow: '0 6px 16px rgba(0,0,0,0.12)',
                  padding: '12px',
                  backgroundColor: 'white'
                }}
                labelStyle={{ fontWeight: '600', color: '#374151', marginBottom: '4px' }}
                itemStyle={{ color: '#6366f1', fontWeight: '500' }}
              />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="#6366f1" 
                strokeWidth={3} 
                fillOpacity={1} 
                fill="url(#colorValue)" 
                activeDot={{ r: 8, stroke: '#6366f1', strokeWidth: 2, fill: 'white' }} 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-8 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center mr-3">
              <Target size={16} className="text-indigo-600" />
            </div>
            <h3 className="font-semibold text-gray-800">关键洞察</h3>
          </div>
          <ul className="space-y-3">
            <li className="flex items-start gap-3">
              <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-2 shrink-0"></div>
              <p className="text-sm text-gray-700 leading-relaxed">数据呈现明显的季节性波动趋势，可据此调整营销策略。</p>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-2 shrink-0"></div>
              <p className="text-sm text-gray-700 leading-relaxed">峰值出现在近期，表明策略调整有效，应继续保持。</p>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-2 shrink-0"></div>
              <p className="text-sm text-gray-700 leading-relaxed">AI 建议：保持当前增长势头，重点关注用户留存率和转化漏斗优化。</p>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ReportView;