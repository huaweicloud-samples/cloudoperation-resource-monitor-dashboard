import os

# 数据库配置
DB_PATH = os.getenv("HWCloud_DB_PATH", "hwcloud_resource_monitor.db")

# 服务端口
SERVER_PORT = int(os.getenv("HWCloud_SERVER_PORT", "8080"))

# 定时任务 Cron 表达式（默认每天凌晨2点）
SCHEDULER_CRON = os.getenv("HWCloud_SCHEDULER_CRON", "0 0 2 * * ?")

# CPU 架构规格列表
X86_SPECS = os.getenv(
    "HWCloud_CPU_ARCH_X86_SPECS",
    "s7.small.1,s7.medium.2,s7.large.2,s7.xlarge.2,s7.2xlarge.2,s7.medium.4,s7.large.4,s7.xlarge.4,s7.2xlarge.4,"
    "s6.small.1,s6.medium.2,s6.large.2,s6.xlarge.2,s6.2xlarge.2,s6.medium.4,s6.large.4,s6.xlarge.4,s6.2xlarge.4,"
    "sn3.small.1,sn3.medium.2,sn3.large.2,sn3.xlarge.2,sn3.2xlarge.2,sn3.4xlarge.2,sn3.medium.4,sn3.large.4,sn3.xlarge.4,sn3.2xlarge.4,sn3.4xlarge.4,"
    "s3.small.1,s3.medium.2,s3.large.2,s3.xlarge.2,s3.2xlarge.2,s3.4xlarge.2,s3.medium.4,s3.large.4,s3.xlarge.4,s3.2xlarge.4,s3.4xlarge.4,"
    "s2.small.1,s2.medium.2,s2.large.2,s2.xlarge.2,s2.2xlarge.2,s2.4xlarge.2,s2.8xlarge.2,s2.medium.4,s2.large.4,s2.xlarge.4,s2.2xlarge.4,s2.4xlarge.4,s2.8xlarge.4,"
    "c7.large.2,c7.xlarge.2,c7.2xlarge.2,c7.3xlarge.2,c7.4xlarge.2,c7.6xlarge.2,c7.8xlarge.2,c7.12xlarge.2,c7.16xlarge.2,c7.24xlarge.2,c7.32xlarge.2,"
    "c7.large.4,c7.xlarge.4,c7.2xlarge.4,c7.3xlarge.4,c7.4xlarge.4,c7.6xlarge.4,c7.8xlarge.4,c7.12xlarge.4,c7.16xlarge.4,c7.24xlarge.4,c7.32xlarge.4,"
    "c6s.large.2,c6s.xlarge.2,c6s.2xlarge.2,c6s.3xlarge.2,c6s.4xlarge.2,c6s.6xlarge.2,c6s.8xlarge.2,c6s.12xlarge.2,c6s.16xlarge.2,"
    "c6.large.2,c6.xlarge.2,c6.2xlarge.2,c6.3xlarge.2,c6.4xlarge.2,c6.6xlarge.2,c6.8xlarge.2,c6.12xlarge.2,c6.16xlarge.2,c6.22xlarge.2,c6.22xlarge.2.physical,"
    "c6.large.4,c6.xlarge.4,c6.2xlarge.4,c6.3xlarge.4,c6.4xlarge.4,c6.6xlarge.4,c6.8xlarge.4,c6.12xlarge.4,c6.16xlarge.4,c6.22xlarge.4,c6.22xlarge.4.physical,"
    "c3ne.large.2,c3ne.xlarge.2,c3ne.2xlarge.2,c3ne.4xlarge.2,c3ne.8xlarge.2,c3ne.15xlarge.2,c3ne.large.4,c3ne.xlarge.4,c3ne.2xlarge.4,c3ne.4xlarge.4,c3ne.8xlarge.4,c3ne.15xlarge.4,"
    "c3.large.2,c3.xlarge.2,c3.2xlarge.2,c3.3xlarge.2,c3.4xlarge.2,c3.6xlarge.2,c3.8xlarge.2,c3.15xlarge.2,c3.large.4,c3.xlarge.4,c3.2xlarge.4,c3.3xlarge.4,c3.4xlarge.4,c3.6xlarge.4,c3.8xlarge.4,c3.15xlarge.4,"
    "t6.small.1,t6.large.1,t6.xlarge.1,t6.2xlarge.1,t6.4xlarge.1,t6.medium.2,t6.large.2,t6.xlarge.2,t6.2xlarge.2,t6.4xlarge.2,t6.large.4,t6.xlarge.4,t6.2xlarge.4,"
    "m7.large.8,m7.xlarge.8,m7.2xlarge.8,m7.3xlarge.8,m7.4xlarge.8,m7.6xlarge.8,m7.8xlarge.8,m7.12xlarge.8,m7.16xlarge.8,m7.24xlarge.8,m7.32xlarge.8,"
    "m6.large.8,m6.xlarge.8,m6.2xlarge.8,m6.3xlarge.8,m6.4xlarge.8,m6.6xlarge.8,m6.8xlarge.8,m6.12xlarge.8,m6.16xlarge.8,m6.22xlarge.8.physical,"
    "m3ne.large.8,m3ne.xlarge.8,m3ne.2xlarge.8,m3ne.3xlarge.8,m3ne.4xlarge.8,m3ne.6xlarge.8,m3ne.8xlarge.8,m3ne.15xlarge.8,"
    "m3.large.8,m3.xlarge.8,m3.2xlarge.8,m3.3xlarge.8,m3.4xlarge.8,m3.6xlarge.8,m3.8xlarge.8,m3.15xlarge.8,"
    "m2.large.8,m2.xlarge.8,m2.2xlarge.8,m2.4xlarge.8,m2.8xlarge.8,"
    "e7.12xlarge.20,e7.24xlarge.20,e6.26xlarge.28,e6.52xlarge.28,e3.7xlarge.12,e3.14xlarge.12,e3.26xlarge.14,e3.52xlarge.14,e3.52xlarge.20,"
    "d7.xlarge.4,d7.2xlarge.4,d7.4xlarge.4,d7.6xlarge.4,d7.8xlarge.4,d7.12xlarge.4,d7.16xlarge.4,"
    "d6.xlarge.4,d6.2xlarge.4,d6.4xlarge.4,d6.6xlarge.4,d6.8xlarge.4,d6.12xlarge.4,d6.16xlarge.4,d6.18xlarge.4,"
    "d3.xlarge.8,d3.2xlarge.8,d3.4xlarge.8,d3.6xlarge.8,d3.8xlarge.8,d3.12xlarge.8,d3.14xlarge.10,"
    "d2.xlarge.8,d2.2xlarge.8,d2.4xlarge.8,d2.6xlarge.8,d2.8xlarge.8,d2.12xlarge.8,"
    "ir7.large.4,ir7.xlarge.4,ir7.2xlarge.4,ir7.4xlarge.4,ir7.8xlarge.4,ir7.16xlarge.4,"
    "i7.2xlarge.4,i7.4xlarge.4,i7.8xlarge.4,i7.12xlarge.4,i7.16xlarge.4,i7.24xlarge.4,"
    "ir3.large.4,ir3.xlarge.4,ir3.2xlarge.4,ir3.4xlarge.4,ir3.8xlarge.4,"
    "i3.2xlarge.8,i3.4xlarge.8,i3.8xlarge.8,i3.12xlarge.8,i3.15xlarge.8,i3.16xlarge.8,"
    "h3.large.2,h3.xlarge.2,h3.2xlarge.2,h3.3xlarge.2,h3.4xlarge.2,h3.6xlarge.2,h3.8xlarge.2,"
    "h3.large.4,h3.xlarge.4,h3.2xlarge.4,h3.3xlarge.4,h3.4xlarge.4,h3.6xlarge.4,h3.8xlarge.4,"
    "hc2.large.2,hc2.xlarge.2,hc2.2xlarge.2,hc2.4xlarge.2,hc2.8xlarge.2,hc2.large.4,hc2.xlarge.4,hc2.2xlarge.4,hc2.4xlarge.4,hc2.8xlarge.4,"
    "h2.3xlarge.10,h2.3xlarge.20,"
    "g6v.2xlarge.2,g6v.2xlarge.4,g6v.4xlarge.4,g6.xlarge.4,g6.4xlarge.4,g6.6xlarge.4,g6.9xlarge.7,g6.18xlarge.7,"
    "g5.8xlarge.4,g3.4xlarge.4,g3.8xlarge.4,g1.xlarge,g1.xlarge.4,g1.2xlarge,g1.2xlarge.8,g1.4xlarge,"
    "p2vs.2xlarge.8,p2vs.4xlarge.8,p2vs.8xlarge.8,p2vs.16xlarge.8,"
    "p2s.2xlarge.8,p2s.4xlarge.8,p2s.8xlarge.8,p2s.16xlarge.8,"
    "p2v.2xlarge.8,p2v.4xlarge.8,p2v.8xlarge.8,p2v.16xlarge.8,"
    "p1.2xlarge.8,p1.4xlarge.8,p1.8xlarge.8,"
    "pi2.2xlarge.4,pi2.4xlarge.4,pi2.8xlarge.4,pi1.2xlarge.4,pi1.4xlarge.4,pi1.8xlarge.4,"
    "ai1s.3xlarge.2,ai1s.4xlarge.2,ai1s.5xlarge.2,ai1s.9xlarge.2,ai1s.large.4,ai1s.xlarge.4,ai1s.2xlarge.4,ai1s.4xlarge.4,ai1s.8xlarge.4,"
    "ai1.large.4,ai1.xlarge.4,ai1.2xlarge.4,ai1.4xlarge.4,ai1.8xlarge.4,"
    "s6.4xlarge.2,s6.4xlarge.4"
)

AARCH64_SPECS = os.getenv(
    "HWCloud_CPU_ARCH_AARCH64_SPECS",
    "kc1.small.1,kc1.large.2,kc1.xlarge.2,kc1.2xlarge.2,kc1.3xlarge.2,kc1.4xlarge.2,kc1.6xlarge.2,kc1.8xlarge.2,kc1.12xlarge.2,kc1.15xlarge.2,"
    "kc1.large.4,kc1.xlarge.4,kc1.2xlarge.4,kc1.3xlarge.4,kc1.4xlarge.4,kc1.6xlarge.4,kc1.8xlarge.4,kc1.12xlarge.4,"
    "km1.large.8,km1.xlarge.8,km1.2xlarge.8,km1.3xlarge.8,km1.4xlarge.8,km1.6xlarge.8,km1.8xlarge.8,km1.12xlarge.8,km1.15xlarge.8,"
    "ki1.2xlarge.4,ki1.4xlarge.4,ki1.6xlarge.4,ki1.8xlarge.4,ki1.12xlarge.4,ki1.16xlarge.4,"
    "kai1s.xlarge.1,kai1s.2xlarge.1,kai1s.4xlarge.1,kai1s.3xlarge.2,kai1s.4xlarge.2,kai1s.6xlarge.2,kai1s.9xlarge.2,kai1s.12xlarge.2"
)

IES_SPECS = os.getenv(
    "HWCloud_CPU_ARCH_IES_SPECS",
    "s7n.large.2,s7n.xlarge.2,s7n.2xlarge.2,s7n.4xlarge.2,s7n.medium.4,s7n.large.4,s7n.xlarge.4,s7n.2xlarge.4,s7n.4xlarge.4,"
    "s6.small.1,s6.medium.2,s6.large.2,s6.xlarge.2,s6.2xlarge.2,s6.medium.4,s6.large.4,s6.xlarge.4,s6.2xlarge.4,"
    "c7n.large.4,c7n.xlarge.4,c7n.2xlarge.4,c7n.3xlarge.4,c7n.4xlarge.4,c7n.6xlarge.4,c7n.8xlarge.4,c7n.12xlarge.4,c7n.16xlarge.4,c7n.24xlarge.4,"
    "c6s.large.2,c6s.large.4,c6s.xlarge.2,c6s.xlarge.4,c6s.2xlarge.2,c6s.2xlarge.4,c6s.3xlarge.2,c6s.3xlarge.4,c6s.4xlarge.2,c6s.4xlarge.4,"
    "c6s.6xlarge.2,c6s.6xlarge.4,c6s.8xlarge.2,c6s.8xlarge.4,c6s.12xlarge.2,c6s.12xlarge.4,c6s.16xlarge.2,c6s.16xlarge.4,"
    "c6sne.large.2,c6sne.large.4,c6sne.xlarge.2,c6sne.xlarge.4,c6sne.2xlarge.2,c6sne.2xlarge.4,c6sne.3xlarge.2,c6sne.3xlarge.4,"
    "c6sne.4xlarge.2,c6sne.4xlarge.4,c6sne.6xlarge.2,c6sne.6xlarge.4,c6sne.8xlarge.2,c6sne.8xlarge.4,c6sne.12xlarge.2,c6sne.12xlarge.4,c6sne.16xlarge.2,c6sne.16xlarge.4,"
    "m7n.large.8,m7n.xlarge.8,m7n.2xlarge.8,m7n.3xlarge.8,m7n.4xlarge.8,m7n.6xlarge.8,m7n.8xlarge.8,m7n.12xlarge.8,m7n.16xlarge.8,m7n.24xlarge.8,"
    "m6s.large.8,m6s.xlarge.8,m6s.2xlarge.8,m6s.3xlarge.8,m6s.4xlarge.8,m6s.6xlarge.8,m6s.8xlarge.8,m6s.16xlarge.8,"
    "d6.xlarge.4,d6.2xlarge.4,d6.4xlarge.4,d6.6xlarge.4,d6.8xlarge.4,d6.12xlarge.4,d6.16xlarge.4,d6.18xlarge.4,"
    "i7n.2xlarge.4,i7n.4xlarge.4,i7n.8xlarge.4,i7n.12xlarge.4,i7n.16xlarge.4,i7n.24xlarge.4,"
    "i3.2xlarge.4,i3.4xlarge.4,i3.8xlarge.4,i3.12xlarge.4,i3.16xlarge.4,"
    "pi2.2xlarge.4,pi2.4xlarge.4,pi2.8xlarge.4"
)


def get_x86_specs_set():
    return set(s.strip() for s in X86_SPECS.split(",") if s.strip())


def get_aarch64_specs_set():
    return set(s.strip() for s in AARCH64_SPECS.split(",") if s.strip())


def get_ies_specs_set():
    return set(s.strip() for s in IES_SPECS.split(",") if s.strip())
