<script setup lang="ts">
import { ref, onMounted } from "vue";
import api from "@/services/api";

const disputes = ref<any[]>([]);
const metrics = ref({
  totalOrders: 0,
  totalVolume: 0,
  activeAuctions: 0,
});

onMounted(async () => {
  // Fetch disputes
  const disputesRes = await api.get("/order/disputes/");
  disputes.value = disputesRes.data;

  // Fetch metrics (mocked or real endpoints)
  // const metricsRes = await api.get('/admin/metrics')
  // metrics.value = metricsRes.data
});
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <h1 class="text-3xl font-bold mb-6">Admin Dashboard</h1>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <dt class="text-sm font-medium text-gray-500 truncate">
            Total Disputes
          </dt>
          <dd class="mt-1 text-3xl font-semibold text-gray-900">
            {{ disputes.length }}
          </dd>
        </div>
      </div>
      <!-- More metrics cards -->
    </div>

    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900">
          Recent Disputes
        </h3>
      </div>
      <div class="border-t border-gray-200">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                ID
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Reason
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Status
              </th>
              <th
                class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Action
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="dispute in disputes" :key="dispute.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ dispute.id }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ dispute.reason }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ dispute.status }}
              </td>
              <td
                class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
              >
                <a href="#" class="text-indigo-600 hover:text-indigo-900"
                  >View</a
                >
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
