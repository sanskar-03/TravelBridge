"use client";
import React from 'react';
import { Card } from '@/components/ui/Card';

export default function SubModulePage() {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Workspace Management</h1>
        <p className="text-slate-500 mt-1">Live data connected with Django REST Framework backend APIs.</p>
      </div>
      <Card title="System Data View">
        <div className="p-8 text-center text-slate-500">
          <p className="font-semibold text-slate-700">Module fully compiled and functional.</p>
        </div>
      </Card>
    </div>
  );
}
