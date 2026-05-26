"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { apiRequest } from "@/lib/api";
import { EvmMetrics } from "@/types";

export function useEvm(projectId: string | null, asOfDate?: string) {
  const { getToken } = useAuth();
  return useQuery<EvmMetrics>({
    queryKey: ["evm", projectId, asOfDate],
    queryFn: async () => {
      const token = await getToken();
      const query = asOfDate ? `?as_of_date=${asOfDate}` : "";
      const data = await apiRequest<any>(
        `/evm/project/${projectId}${query}`,
        {},
        token ?? undefined
      );
      const cv = data.ev - data.ac;
      const sv = data.ev - data.pv;
      const etc = data.bac - data.ev;
      const tcpi = etc > 0 ? (data.bac - data.ev) / (data.bac - data.ac) : 1.0;
      return {
        pv: data.pv,
        ev: data.ev,
        ac: data.ac,
        cv: roundToTwo(cv),
        sv: roundToTwo(sv),
        cpi: data.cpi,
        spi: data.spi,
        eac: data.eac,
        etc: roundToTwo(etc),
        tcpi: roundToTwo(tcpi),
      };
    },
    enabled: !!projectId,
  });
}

function roundToTwo(num: number): number {
  return Math.round((num + Number.EPSILON) * 100) / 100;
}
