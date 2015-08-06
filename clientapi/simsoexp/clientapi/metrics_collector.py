import numpy as np

class MetricsCollector(object):
    """
    Class used to collect metrics from results"""
    def __init__(self, result):
        self.metrics = {}
        self.metrics["task_migrations"] = sum(task.task_migration_count for task in
                                   result.tasks.values())
        self.metrics["migrations"] = 0
        self.metrics["preemptions"] = 0
        self.metrics["preemptions_inter"] = 0

        cycles_per_ms = result.model.cycles_per_ms

        for task in result.tasks.values():
            self.metrics["migrations"] += sum(job.migration_count for job in task.jobs)
            self.metrics["preemptions"] += sum(job.preemption_count for job in task.jobs)
            self.metrics["preemptions_inter"] += sum(job.preemption_inter_count
                                          for job in task.jobs)

        self.metrics["deadline_misses"] = sum(task.exceeded_count for task in
                                  result.tasks.values())

        self.metrics["response_time"] = 0
        for task in result.tasks.values():
            self.metrics["response_time"] += sum((job.response_time for job in task.jobs
                                       if job.response_time)) / len(task.jobs)
        self.metrics["response_time"] = (self.metrics["response_time"] / (len(result.tasks)
                              * cycles_per_ms))

        normalised_laxities = np.array(
            [(task.task.deadline - float(job.response_time) / cycles_per_ms)
             / task.task.period
             for task in result.tasks.values()
             for job in task.jobs
             if job.response_time and not job.aborted])
        self.metrics["avg_laxities"] = normalised_laxities.mean()
        self.metrics["std_laxities"] = normalised_laxities.std()
        self.metrics["job_count"] = len(normalised_laxities)
        self.metrics["on_schedule_count"] = result.scheduler.schedule_count
        self.metrics["timers"] = result.total_timers